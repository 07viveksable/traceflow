from datetime import datetime

from sqlalchemy.orm import Session

from app.metric_models import PipelineMetric


def create_metric(
    db: Session,
    run_id: str,
    execution_time: float,
    records_processed: int,
    records_failed: int,
    status: str
):

    metric = PipelineMetric(
        run_id=run_id,
        execution_time=execution_time,
        records_processed=records_processed,
        records_failed=records_failed,
        status=status,
        created_at=datetime.now()
    )

    db.add(metric)

    db.commit()

    db.refresh(metric)

    return metric


def get_metrics_by_run_id(
    db: Session,
    run_id: str
):

    return (
        db.query(PipelineMetric)
        .filter(
            PipelineMetric.run_id == run_id
        )
        .order_by(
            PipelineMetric.created_at.asc()
        )
        .all()
    )


def get_all_metrics(db: Session):

    return (
        db.query(PipelineMetric)
        .order_by(
            PipelineMetric.created_at.desc()
        )
        .all()
    )