from datetime import datetime

from sqlalchemy.orm import Session

from app.models import PipelineRun


def create_run(
    db: Session,
    run_id: str,
    pipeline_name: str,
    user_id: int
):
    run = PipelineRun(
        run_id=run_id,
        pipeline_name=pipeline_name,
        status="RUNNING",
        records_processed=0,
        start_time=datetime.now(),
        user_id=user_id
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    return run


def get_all_runs(db: Session):

    return (
        db.query(PipelineRun)
        .order_by(
            PipelineRun.start_time.desc()
        )
        .all()
    )


def get_run_by_id(
    db: Session,
    run_id: str
):

    return (
        db.query(PipelineRun)
        .filter(
            PipelineRun.run_id == run_id
        )
        .first()
    )


def update_run_success(
    db: Session,
    run_id: str,
    records_processed: int
):

    run = get_run_by_id(
        db,
        run_id
    )

    if run:

        run.status = "SUCCESS"

        run.records_processed = (
            records_processed
        )

        run.end_time = datetime.now()

        run.error_message = None

        db.commit()
        db.refresh(run)

    return run


def update_run_failed(
    db: Session,
    run_id: str,
    error_message: str
):

    run = get_run_by_id(
        db,
        run_id
    )

    if run:

        run.status = "FAILED"

        run.end_time = datetime.now()

        run.error_message = error_message

        db.commit()
        db.refresh(run)

    return run


def delete_run(
    db: Session,
    run_id: str
):

    run = get_run_by_id(
        db,
        run_id
    )

    if run:

        db.delete(run)

        db.commit()

        return True

    return False