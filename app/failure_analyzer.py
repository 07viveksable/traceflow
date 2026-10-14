from sqlalchemy.orm import Session

from app.log_models import PipelineLog


def analyze_failure(
    db: Session,
    run_id: str,
    error_message: str | None = None
):

    # ------------------------------------------------
    # Get ERROR logs
    # ------------------------------------------------

    error_logs = (
        db.query(PipelineLog)
        .filter(
            PipelineLog.run_id == run_id,
            PipelineLog.level == "ERROR"
        )
        .order_by(
            PipelineLog.timestamp.desc()
        )
        .all()
    )

    # ------------------------------------------------
    # Build searchable error text
    # ------------------------------------------------

    messages = []

    for log in error_logs:
        messages.append(log.message)

    if error_message:
        messages.append(error_message)

    combined_error = " ".join(
        messages
    ).lower()

    # ------------------------------------------------
    # Rule 1: File not found
    # ------------------------------------------------

    if (
        "no such file or directory"
        in combined_error
        or
        "filenotfounderror"
        in combined_error
        or
        "file not found"
        in combined_error
    ):

        return {
            "fingerprint": "FILE_NOT_FOUND",

            "root_cause": (
                "The configured input file "
                "does not exist."
            ),

            "suggested_action": (
                "Verify the input file path "
                "in config/config.json "
                "and make sure the file exists."
            ),

            "confidence": 0.98
        }

    # ------------------------------------------------
    # Rule 2: Permission denied
    # ------------------------------------------------

    if (
        "permission denied"
        in combined_error
        or
        "permissionerror"
        in combined_error
        or
        "access is denied"
        in combined_error
    ):

        return {
            "fingerprint": "PERMISSION_DENIED",

            "root_cause": (
                "The application does not have "
                "permission to access the required "
                "file or resource."
            ),

            "suggested_action": (
                "Check file permissions and "
                "application access rights."
            ),

            "confidence": 0.97
        }

    # ------------------------------------------------
    # Rule 3: Database error
    # ------------------------------------------------

    if (
        "mysql"
        in combined_error
        or
        "database"
        in combined_error
        or
        "connection refused"
        in combined_error
        or
        "connection error"
        in combined_error
    ):

        return {
            "fingerprint": "DATABASE_ERROR",

            "root_cause": (
                "The application encountered "
                "a database connectivity or "
                "database operation problem."
            ),

            "suggested_action": (
                "Check whether MySQL is running "
                "and verify the database configuration "
                "in the .env file."
            ),

            "confidence": 0.95
        }

    # ------------------------------------------------
    # Rule 4: Invalid data
    # ------------------------------------------------

    if (
        "invalid amount"
        in combined_error
        or
        "invalid data"
        in combined_error
        or
        "valueerror"
        in combined_error
        or
        "could not convert"
        in combined_error
    ):

        return {
            "fingerprint": "INVALID_DATA",

            "root_cause": (
                "The pipeline received data "
                "that does not match the expected format."
            ),

            "suggested_action": (
                "Validate the input CSV and "
                "correct invalid values before "
                "running the pipeline."
            ),

            "confidence": 0.93
        }

    # ------------------------------------------------
    # Rule 5: Timeout
    # ------------------------------------------------

    if (
        "timeout"
        in combined_error
        or
        "timed out"
        in combined_error
    ):

        return {
            "fingerprint": "TIMEOUT",

            "root_cause": (
                "A pipeline operation took longer "
                "than the allowed time."
            ),

            "suggested_action": (
                "Check the slow operation, "
                "database performance, or external "
                "service availability."
            ),

            "confidence": 0.92
        }

    # ------------------------------------------------
    # Rule 6: Unknown error
    # ------------------------------------------------

    return {
        "fingerprint": "UNKNOWN_ERROR",

        "root_cause": (
            "The pipeline failed due to an "
            "unrecognized error condition."
        ),

        "suggested_action": (
            "Review the pipeline logs and "
            "investigate the error manually."
        ),

        "confidence": 0.60
    }