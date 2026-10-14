from sqlalchemy.orm import Session

from app.models import PipelineRun
from app.log_models import PipelineLog
from app.metric_models import PipelineMetric

from app.incident_repository import create_incident


# Execution time above this value
# will be considered unusually slow.
SLOW_EXECUTION_THRESHOLD = 5.0


def detect_failure(
    db: Session,
    run_id: str
):

    run = (
        db.query(PipelineRun)
        .filter(
            PipelineRun.run_id == run_id
        )
        .first()
    )

    if run is None:
        return None

    # ------------------------------------------------
    # RULE 1: Pipeline failed
    # ------------------------------------------------

    if run.status == "FAILED":

        incident = create_incident(
            db=db,
            run_id=run_id,
            incident_type="PIPELINE_FAILURE",
            severity="HIGH",
            title="Pipeline execution failed",
            description=(
                run.error_message
                or
                "Pipeline execution failed."
            )
        )

        return incident

    # ------------------------------------------------
    # Get latest metric
    # ------------------------------------------------

    metric = (
        db.query(PipelineMetric)
        .filter(
            PipelineMetric.run_id == run_id
        )
        .order_by(
            PipelineMetric.created_at.desc()
        )
        .first()
    )

    # ------------------------------------------------
    # RULE 2: Failed records
    # ------------------------------------------------

    if metric is not None:

        if metric.records_failed > 0:

            incident = create_incident(
                db=db,
                run_id=run_id,
                incident_type="RECORD_FAILURE",
                severity="MEDIUM",
                title="Records failed during pipeline execution",
                description=(
                    f"{metric.records_failed} "
                    f"record(s) failed during processing."
                )
            )

            return incident

        # ------------------------------------------------
        # RULE 3: Slow pipeline
        # ------------------------------------------------

        if (
            metric.execution_time
            > SLOW_EXECUTION_THRESHOLD
        ):

            incident = create_incident(
                db=db,
                run_id=run_id,
                incident_type="PERFORMANCE_ANOMALY",
                severity="MEDIUM",
                title="Pipeline execution is unusually slow",
                description=(
                    f"Pipeline execution took "
                    f"{metric.execution_time:.4f} seconds, "
                    f"which is above the configured "
                    f"threshold of "
                    f"{SLOW_EXECUTION_THRESHOLD} seconds."
                )
            )

            return incident

    # ------------------------------------------------
    # RULE 4: ERROR log
    # ------------------------------------------------

    error_log = (
        db.query(PipelineLog)
        .filter(
            PipelineLog.run_id == run_id,
            PipelineLog.level == "ERROR"
        )
        .first()
    )

    if error_log is not None:

        incident = create_incident(
            db=db,
            run_id=run_id,
            incident_type="ERROR_DETECTED",
            severity="HIGH",
            title="Error detected in pipeline logs",
            description=error_log.message
        )

        return incident

    return None