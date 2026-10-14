from datetime import datetime

from sqlalchemy.orm import Session

from app.incident_models import Incident


def create_incident(
    db: Session,
    run_id: str,
    incident_type: str,
    severity: str,
    title: str,
    description: str
):
    incident = Incident(
        run_id=run_id,
        incident_type=incident_type,
        severity=severity,
        title=title,
        description=description,
        status="OPEN",
        created_at=datetime.now()
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident


def get_all_incidents(db: Session):

    return (
        db.query(Incident)
        .order_by(
            Incident.created_at.desc()
        )
        .all()
    )


def get_incident_by_id(
    db: Session,
    incident_id: int
):

    return (
        db.query(Incident)
        .filter(
            Incident.id == incident_id
        )
        .first()
    )


def get_incident_by_run_id(
    db: Session,
    run_id: str
):

    return (
        db.query(Incident)
        .filter(
            Incident.run_id == run_id
        )
        .order_by(
            Incident.created_at.desc()
        )
        .first()
    )


def resolve_incident(
    db: Session,
    incident_id: int
):

    incident = get_incident_by_id(
        db,
        incident_id
    )

    if incident:

        incident.status = "RESOLVED"

        incident.resolved_at = datetime.now()

        db.commit()

        db.refresh(incident)

    return incident