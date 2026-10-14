
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.log_models import PipelineLog


def create_log(db: Session, run_id: str, level: str, message: str):
    """Create and save a pipeline log."""

    log = PipelineLog(
        run_id=run_id,
        level=level,
        message=message,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


def get_logs_by_run_id(db: Session, run_id: str):
    """Return logs for a specific pipeline run."""

    return (
        db.query(PipelineLog)
        .filter(PipelineLog.run_id == run_id)
        .order_by(PipelineLog.timestamp.desc())
        .all()
    )


def search_pipeline_logs(
    db: Session,
    run_id: str | None = None,
    level: str | None = None,
    keyword: str | None = None,
    limit: int = 100,
):
    """Search pipeline logs by run ID, severity, and message."""

    query = db.query(PipelineLog)

    if run_id:
        query = query.filter(PipelineLog.run_id == run_id)

    if level:
        query = query.filter(
            func.upper(PipelineLog.level) == level.upper()
        )

    if keyword:
        query = query.filter(
            PipelineLog.message.ilike(f"%{keyword}%")
        )

    return (
        query
        .order_by(PipelineLog.timestamp.desc())
        .limit(limit)
        .all()
    )
