def decide_recovery(fingerprint: str):

    fingerprint = fingerprint.upper()

    # ---------------------------------
    # LOW RISK
    # ---------------------------------

    if fingerprint == "TIMEOUT":

        return {
            "action": "AUTO_RETRY",
            "risk_level": "LOW",
            "status": "READY",
            "message": (
                "Timeout detected. "
                "The pipeline is eligible for "
                "a safe retry."
            )
        }

    # ---------------------------------
    # MEDIUM RISK
    # ---------------------------------

    if fingerprint == "DATABASE_ERROR":

        return {
            "action": "DATABASE_RECONNECT",
            "risk_level": "MEDIUM",
            "status": "APPROVAL_REQUIRED",
            "message": (
                "Database error detected. "
                "Database reconnection requires "
                "human approval before execution."
            )
        }

    # ---------------------------------
    # HIGH RISK
    # ---------------------------------

    if fingerprint == "FILE_NOT_FOUND":

        return {
            "action": "MANUAL_INTERVENTION",
            "risk_level": "HIGH",
            "status": "BLOCKED",
            "message": (
                "Input file was not found. "
                "Manual intervention is required."
            )
        }

    if fingerprint == "PERMISSION_DENIED":

        return {
            "action": "MANUAL_INTERVENTION",
            "risk_level": "HIGH",
            "status": "BLOCKED",
            "message": (
                "Permission problem detected. "
                "Manual permission correction is required."
            )
        }

    if fingerprint == "INVALID_DATA":

        return {
            "action": "MANUAL_INTERVENTION",
            "risk_level": "HIGH",
            "status": "BLOCKED",
            "message": (
                "Invalid input data detected. "
                "The data must be corrected before "
                "the pipeline can be retried."
            )
        }

    # ---------------------------------
    # UNKNOWN ERROR
    # ---------------------------------

    return {
        "action": "MANUAL_INTERVENTION",
        "risk_level": "HIGH",
        "status": "BLOCKED",
        "message": (
            "The failure type is unknown. "
            "Manual investigation is required."
        )
    }


def execute_recovery(
    fingerprint: str,
    action: str
):

    fingerprint = fingerprint.upper()

    # ---------------------------------
    # SAFE SIMULATION
    # ---------------------------------

    if (
        fingerprint == "TIMEOUT"
        and action == "AUTO_RETRY"
    ):

        return {
            "status": "SIMULATED_SUCCESS",
            "message": (
                "Recovery retry was simulated "
                "successfully. "
                "The actual pipeline retry will be "
                "implemented in a later version."
            )
        }

    if action == "DATABASE_RECONNECT":

        return {
            "status": "WAITING_FOR_APPROVAL",
            "message": (
                "Database reconnection requires "
                "human approval."
            )
        }

    return {
        "status": "BLOCKED",
        "message": (
            "Automatic recovery is not allowed "
            "for this failure type."
        )
    }