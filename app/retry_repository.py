from datetime import datetime

from sqlalchemy.orm import Session

from app.retry_models import RetryAttempt


def count_retries_for_incident(
    db: Session,
    incident_id: int    
) -> int:

    return (
        db.query(RetryAttempt)
        .filter(
            RetryAttempt.incident_id == incident_id
        )
        .count()
    )


def create_retry_attempt(
    db: Session,
    incident_id: int,
    run_id: str,
    attempt_number: int,
    delay_seconds: int,
    status: str,
    message: str
):

    attempt = RetryAttempt(
        incident_id=incident_id,
        run_id=run_id,
        attempt_number=attempt_number,
        delay_seconds=delay_seconds,
        status=status,
        message=message,
        created_at=datetime.now()
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt


def update_retry_attempt(
    db: Session,
    attempt_id: int,
    status: str,
    message: str
):

    attempt = (
        db.query(RetryAttempt)
        .filter(
            RetryAttempt.id == attempt_id
        )
        .first()
    )

    if attempt is None:
        return None

    attempt.status = status
    attempt.message = message
    attempt.completed_at = datetime.now()

    db.commit()
    db.refresh(attempt)

    return attempt


def get_all_retry_attempts(
    db: Session
):

    return (
        db.query(RetryAttempt)
        .order_by(
            RetryAttempt.created_at.desc()
        )
        .all()
    )


def get_retry_attempt_by_id(
    db: Session,
    attempt_id: int
):

    return (
        db.query(RetryAttempt)
        .filter(
            RetryAttempt.id == attempt_id
        )
        .first()
    )


def get_retries_by_incident_id(
    db: Session,
    incident_id: int
):

    return (
        db.query(RetryAttempt)
        .filter(
            RetryAttempt.incident_id == incident_id
        )
        .order_by(
            RetryAttempt.attempt_number.asc()
        )
        .all()
    )


def get_retries_by_run_id(
    db: Session,
    run_id: str
):

    return (
        db.query(RetryAttempt)
        .filter(
            RetryAttempt.run_id == run_id
        )
        .order_by(
            RetryAttempt.created_at.desc()
        )
        .all()
    )