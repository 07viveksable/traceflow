from datetime import datetime

from sqlalchemy.orm import Session

from app.root_cause_models import RootCauseAnalysis


def create_root_cause_analysis(
    db: Session,
    incident_id: int,
    run_id: str,
    fingerprint: str,
    root_cause: str,
    suggested_action: str,
    confidence: float
):

    analysis = RootCauseAnalysis(
        incident_id=incident_id,
        run_id=run_id,
        fingerprint=fingerprint,
        root_cause=root_cause,
        suggested_action=suggested_action,
        confidence=confidence,
        created_at=datetime.now()
    )

    db.add(analysis)

    db.commit()

    db.refresh(analysis)

    return analysis


def get_root_cause_by_incident_id(
    db: Session,
    incident_id: int
):

    return (
        db.query(RootCauseAnalysis)
        .filter(
            RootCauseAnalysis.incident_id == incident_id
        )
        .order_by(
            RootCauseAnalysis.created_at.desc()
        )
        .first()
    )


def get_root_causes_by_run_id(
    db: Session,
    run_id: str
):

    return (
        db.query(RootCauseAnalysis)
        .filter(
            RootCauseAnalysis.run_id == run_id
        )
        .order_by(
            RootCauseAnalysis.created_at.desc()
        )
        .all()
    )


def get_all_root_cause_analyses(
    db: Session
):

    return (
        db.query(RootCauseAnalysis)
        .order_by(
            RootCauseAnalysis.created_at.desc()
        )
        .all()
    )