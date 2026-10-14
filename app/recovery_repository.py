from datetime import datetime

from sqlalchemy.orm import Session

from app.recovery_models import RecoveryAttempt


def create_recovery_attempt(
    db: Session,
    incident_id: int,
    run_id: str,
    action: str,
    risk_level: str,
    status: str,
    message: str,
    attempt_number: int = 1
):

    recovery_attempt = RecoveryAttempt(
        incident_id=incident_id,
        run_id=run_id,
        action=action,
        risk_level=risk_level,
        status=status,
        message=message,
        attempt_number=attempt_number,
        created_at=datetime.now()
    )

    db.add(recovery_attempt)

    db.commit()

    db.refresh(recovery_attempt)

    return recovery_attempt


def get_all_recovery_attempts(
    db: Session
):

    return (
        db.query(RecoveryAttempt)
        .order_by(
            RecoveryAttempt.created_at.desc()
        )
        .all()
    )


def get_recovery_attempt_by_id(
    db: Session,
    recovery_id: int
):

    return (
        db.query(RecoveryAttempt)
        .filter(
            RecoveryAttempt.id == recovery_id
        )
        .first()
    )


def get_recovery_attempts_by_incident_id(
    db: Session,
    incident_id: int
):

    return (
        db.query(RecoveryAttempt)
        .filter(
            RecoveryAttempt.incident_id == incident_id
        )
        .order_by(
            RecoveryAttempt.created_at.desc()
        )
        .all()
    )


def get_recovery_attempts_by_run_id(
    db: Session,
    run_id: str
):

    return (
        db.query(RecoveryAttempt)
        .filter(
            RecoveryAttempt.run_id == run_id
        )
        .order_by(
            RecoveryAttempt.created_at.desc()
        )
        .all()
    )


def complete_recovery_attempt(
    db: Session,
    recovery_id: int,
    status: str,
    message: str
):

    recovery_attempt = get_recovery_attempt_by_id(
        db,
        recovery_id
    )

    if recovery_attempt:

        recovery_attempt.status = status

        recovery_attempt.message = message

        recovery_attempt.completed_at = datetime.now()

        db.commit()

        db.refresh(recovery_attempt)

    return recovery_attempt