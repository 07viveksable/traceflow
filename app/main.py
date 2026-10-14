
from datetime import datetime
from time import sleep
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Database and pipeline
from app.database import get_db
from app.config import load_config
from app.pipeline import TraceFlowPipeline

# Models: import all models so SQLAlchemy registers their tables
from app.models import PipelineRun
from app.user_models import User
from app.log_models import PipelineLog
from app.metric_models import PipelineMetric
from app.incident_models import Incident
from app.root_cause_models import RootCauseAnalysis
from app.recovery_models import RecoveryAttempt
from app.retry_models import RetryAttempt

# Authentication
from app.auth import (
    hash_password,
    create_access_token,
    get_current_user,
    authenticate_user,
    require_roles,
)
from app.roles import Role
from app.auth_repository import (
    create_user,
    get_user_by_username,
    get_user_by_email,
)

# Pipeline repository
from app.repository import (
    create_run,
    get_all_runs,
    get_run_by_id,
    update_run_success,
    update_run_failed,
    delete_run,
)

# Logging
from app.log_repository import (
    create_log,
    get_logs_by_run_id,
    search_pipeline_logs,
)

# Metrics
from app.metric_repository import (
    create_metric,
    get_metrics_by_run_id,
    get_all_metrics,
)

# Incidents
from app.incident_repository import (
    create_incident,
    get_all_incidents,
    get_incident_by_id,
    get_incident_by_run_id,
    resolve_incident,
)
from app.failure_detector import detect_failure

# Root-cause analysis
from app.root_cause_repository import (
    create_root_cause_analysis,
    get_root_cause_by_incident_id,
    get_root_causes_by_run_id,
    get_all_root_cause_analyses,
)
from app.failure_analyzer import analyze_failure

# Recovery
from app.recovery_repository import (
    create_recovery_attempt,
    get_all_recovery_attempts,
    get_recovery_attempt_by_id,
    get_recovery_attempts_by_incident_id,
    get_recovery_attempts_by_run_id,
    complete_recovery_attempt,
)
from app.recovery_engine import decide_recovery, execute_recovery

# Retry
from app.retry_repository import (
    count_retries_for_incident,
    create_retry_attempt,
    update_retry_attempt,
    get_all_retry_attempts,
    get_retry_attempt_by_id,
    get_retries_by_incident_id,
    get_retries_by_run_id,
)
from app.retry_engine import get_retry_policy

# Day 25: Retry analytics
from app.retry_analytics import (
    generate_retry_analytics,
    generate_retry_health_report,
)

# Day 29: Pipeline performance analytics
from app.performance_analytics import generate_performance_report


app = FastAPI(
    title="TraceFlow API",
    description="Predictive Data Pipeline Monitoring and Auto-Recovery Platform",
    version="1.0.0",
)


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to TraceFlow API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db),
):
    if get_user_by_username(db, username):
        raise HTTPException(
            status_code=400,
            detail="Username already exists",
        )

    if get_user_by_email(db, email):
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    user = create_user(
        db,
        username=username,
        email=email,
        hashed_password=hash_password(password),
    )

    return {
        "message": "User registered successfully",
        "username": user.username,
        "role": user.role,
    }


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.username)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@app.get("/users/me")
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }


# ---------------------------------------------------------
# PIPELINE EXECUTION
# ---------------------------------------------------------

@app.post("/pipelines/run")
def run_pipeline(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(Role.ADMIN, Role.DEVELOPER)
    ),
):
    run_id = str(uuid4())
    pipeline_name = "TraceFlow Pipeline"
    start_time = datetime.now()

    create_run(
        db,
        run_id=run_id,
        pipeline_name=pipeline_name,
        user_id=current_user.id,
    )
    db.commit()

    try:
        config = load_config()
        pipeline = TraceFlowPipeline(config)
        result = pipeline.run()

        records_processed = (
            result.get("records_processed", 0)
            if isinstance(result, dict)
            else 0
        )

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        update_run_success(
            db,
            run_id,
            records_processed,
        )

        create_log(
            db,
            run_id,
            "INFO",
            "Pipeline completed successfully",
        )

        create_metric(
            db,
            run_id,
            execution_time,
            records_processed,
            0,
            "SUCCESS",
        )

        db.commit()

        detect_failure(db, run_id)
        db.commit()

        return {
            "message": "Pipeline executed successfully",
            "run_id": run_id,
            "status": "SUCCESS",
            "records_processed": records_processed,
            "execution_time": execution_time,
        }

    except Exception as exc:
        db.rollback()

        error_message = str(exc)

        update_run_failed(
            db,
            run_id,
            error_message,
        )

        create_log(
            db,
            run_id,
            "ERROR",
            error_message,
        )

        execution_time = (
            datetime.now() - start_time
        ).total_seconds()

        create_metric(
            db,
            run_id,
            execution_time,
            0,
            1,
            "FAILED",
        )

        db.commit()

        incident = detect_failure(db, run_id)
        db.commit()

        if incident:
            analyze_failure(
                db,
                run_id,
                error_message,
            )
            db.commit()

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Pipeline execution failed",
                "run_id": run_id,
                "error": error_message,
            },
        )


# ---------------------------------------------------------
# PIPELINE RUNS
# ---------------------------------------------------------

@app.get("/runs")
def list_runs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_runs(db)


@app.get("/runs/{run_id}")
def get_run(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = get_run_by_id(db, run_id)

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Pipeline run not found",
        )

    return run


@app.delete("/runs/{run_id}")
def remove_run(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(Role.ADMIN, Role.DEVELOPER)
    ),
):
    run = get_run_by_id(db, run_id)

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Pipeline run not found",
        )

    delete_run(db, run_id)

    return {"message": "Run deleted successfully"}


# ---------------------------------------------------------
# PIPELINE LOGS
# ---------------------------------------------------------

@app.get("/runs/{run_id}/logs")
def get_run_logs(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not get_run_by_id(db, run_id):
        raise HTTPException(
            status_code=404,
            detail="Pipeline run not found",
        )

    return get_logs_by_run_id(db, run_id)


# ---------------------------------------------------------
# DAY 28: ADVANCED LOG SEARCH
# ---------------------------------------------------------

@app.get("/logs/search")
def search_logs(
    run_id: str | None = None,
    level: str | None = None,
    keyword: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_levels = {
        "INFO",
        "WARNING",
        "ERROR",
        "DEBUG",
    }

    if level and level.upper() not in allowed_levels:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid level. Use INFO, WARNING, ERROR, or DEBUG."
            ),
        )

    logs = search_pipeline_logs(
        db=db,
        run_id=run_id,
        level=level,
        keyword=keyword,
        limit=limit,
    )

    return logs


# ---------------------------------------------------------
# PIPELINE METRICS
# ---------------------------------------------------------

@app.get("/metrics")
def list_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_metrics(db)


@app.get("/runs/{run_id}/metrics")
def get_run_metrics(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not get_run_by_id(db, run_id):
        raise HTTPException(
            status_code=404,
            detail="Pipeline run not found",
        )

    return get_metrics_by_run_id(db, run_id)


# ---------------------------------------------------------
# INCIDENT MANAGEMENT
# ---------------------------------------------------------

@app.get("/incidents")
def list_incidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_incidents(db)


@app.get("/incidents/{incident_id}")
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = get_incident_by_id(db, incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


@app.get("/runs/{run_id}/incident")
def get_run_incident(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = get_incident_by_run_id(db, run_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found for this run",
        )

    return incident


@app.patch("/incidents/{incident_id}/resolve")
def resolve_incident_route(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(Role.ADMIN, Role.DEVELOPER)
    ),
):
    incident = get_incident_by_id(db, incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    result = resolve_incident(db, incident_id)
    db.commit()

    return {
        "message": "Incident resolved successfully",
        "incident": result,
    }


# ---------------------------------------------------------
# ROOT-CAUSE ANALYSIS
# ---------------------------------------------------------

@app.get("/root-causes")
def list_root_causes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_root_cause_analyses(db)


@app.get("/incidents/{incident_id}/root-cause")
def get_incident_root_cause(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = get_root_cause_by_incident_id(
        db,
        incident_id,
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Root-cause analysis not found",
        )

    return analysis


@app.get("/runs/{run_id}/root-causes")
def get_run_root_causes(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_root_causes_by_run_id(db, run_id)


# ---------------------------------------------------------
# RECOVERY MANAGEMENT
# ---------------------------------------------------------

@app.get("/recovery-attempts")
def list_recovery_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_recovery_attempts(db)


@app.get("/recovery-attempts/{recovery_id}")
def get_recovery_attempt(
    recovery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = get_recovery_attempt_by_id(
        db,
        recovery_id,
    )

    if not attempt:
        raise HTTPException(
            status_code=404,
            detail="Recovery attempt not found",
        )

    return attempt


@app.get("/incidents/{incident_id}/recovery-attempts")
def get_incident_recovery_attempts(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_recovery_attempts_by_incident_id(
        db,
        incident_id,
    )


@app.get("/runs/{run_id}/recovery-attempts")
def get_run_recovery_attempts(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_recovery_attempts_by_run_id(
        db,
        run_id,
    )


@app.post("/incidents/{incident_id}/recover")
def recover_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(Role.ADMIN, Role.DEVELOPER)
    ),
):
    incident = get_incident_by_id(db, incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    analysis = get_root_cause_by_incident_id(
        db,
        incident_id,
    )

    if not analysis:
        raise HTTPException(
            status_code=400,
            detail="Run root-cause analysis before recovery",
        )

    decision = decide_recovery(analysis.fingerprint)

    attempt = create_recovery_attempt(
        db,
        incident_id=incident_id,
        run_id=incident.run_id,
        action=decision["action"],
        risk_level=decision["risk_level"],
        status=decision["status"],
        message=decision.get(
            "message",
            "Recovery decision created",
        ),
    )

    execution = execute_recovery(
        analysis.fingerprint,
        decision["action"],
    )

    if execution == "SIMULATED_SUCCESS":
        complete_recovery_attempt(
            db,
            attempt.id,
            status="SIMULATED_SUCCESS",
            message="Recovery simulation completed successfully",
        )

    db.commit()

    return {
        "message": "Recovery decision processed",
        "decision": decision,
        "execution_result": execution,
        "attempt": attempt,
    }


# ---------------------------------------------------------
# RETRY MANAGEMENT
# ---------------------------------------------------------

@app.get("/retry-attempts")
def list_retry_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_retry_attempts(db)


@app.get("/retry-attempts/{attempt_id}")
def get_retry_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = get_retry_attempt_by_id(db, attempt_id)

    if not attempt:
        raise HTTPException(
            status_code=404,
            detail="Retry attempt not found",
        )

    return attempt


@app.get("/incidents/{incident_id}/retries")
def get_incident_retries(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_retries_by_incident_id(db, incident_id)


@app.get("/runs/{run_id}/retries")
def get_run_retries(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_retries_by_run_id(db, run_id)


@app.post("/incidents/{incident_id}/retry")
def retry_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(Role.ADMIN, Role.DEVELOPER)
    ),
):
    incident = get_incident_by_id(db, incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    analysis = get_root_cause_by_incident_id(
        db,
        incident_id,
    )

    if not analysis:
        raise HTTPException(
            status_code=400,
            detail="Run root-cause analysis before retrying",
        )

    if analysis.fingerprint.upper() != "TIMEOUT":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only TIMEOUT incidents are eligible for automatic retry"
            ),
        )

    previous_attempts = count_retries_for_incident(
        db,
        incident_id,
    )
    attempt_number = previous_attempts + 1

    policy = get_retry_policy(
        analysis.fingerprint,
        attempt_number,
    )

    if not policy["eligible"]:
        raise HTTPException(
            status_code=400,
            detail=policy["message"],
        )

    retry = create_retry_attempt(
        db,
        incident_id=incident_id,
        run_id=incident.run_id,
        attempt_number=attempt_number,
        delay_seconds=policy["delay_seconds"],
        status="IN_PROGRESS",
        message=policy["message"],
    )

    db.commit()

    try:
        sleep(policy["delay_seconds"])

        retry_run_id = str(uuid4())
        start_time = datetime.now()

        create_run(
            db,
            run_id=retry_run_id,
            pipeline_name="TraceFlow Retry",
            user_id=current_user.id,
        )
        db.commit()

        config = load_config()
        pipeline = TraceFlowPipeline(config)
        result = pipeline.run()

        records_processed = (
            result.get("records_processed", 0)
            if isinstance(result, dict)
            else 0
        )

        execution_time = (
            datetime.now() - start_time
        ).total_seconds()

        update_run_success(
            db,
            retry_run_id,
            records_processed,
        )

        create_log(
            db,
            retry_run_id,
            "INFO",
            f"Retry for incident {incident_id} completed",
        )

        create_metric(
            db,
            retry_run_id,
            execution_time,
            records_processed,
            0,
            "SUCCESS",
        )

        update_retry_attempt(
            db,
            retry.id,
            "SUCCESS",
            f"Retry succeeded. New pipeline run: {retry_run_id}",
        )

        db.commit()

        return {
            "message": "Retry completed successfully",
            "incident_id": incident_id,
            "attempt_number": attempt_number,
            "retry_run_id": retry_run_id,
            "status": "SUCCESS",
        }

    except Exception as exc:
        db.rollback()

        error_message = str(exc)

        update_retry_attempt(
            db,
            retry.id,
            "FAILED",
            error_message,
        )

        db.commit()

        return {
            "message": "Retry failed",
            "incident_id": incident_id,
            "attempt_number": attempt_number,
            "status": "FAILED",
            "error": error_message,
        }


# ---------------------------------------------------------
# DAY 25: RETRY MONITORING AND ANALYTICS
# ---------------------------------------------------------

@app.get("/retry-monitoring/analytics")
def get_retry_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    retry_attempts = get_all_retry_attempts(db)

    return generate_retry_analytics(retry_attempts)


@app.get("/retry-monitoring/health")
def get_retry_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    retry_attempts = get_all_retry_attempts(db)

    incidents = generate_retry_health_report(
        retry_attempts
    )

    return {
        "total_incidents_with_retries": len(
            {
                attempt.incident_id
                for attempt in retry_attempts
            }
        ),
        "incidents": incidents,
    }


# ---------------------------------------------------------
# DAY 29: PIPELINE PERFORMANCE ANALYTICS
# ---------------------------------------------------------

@app.get("/performance/analytics")
def get_performance_analytics(
    slow_threshold: float = Query(
        default=5.0,
        gt=0,
        le=3600,
        description=(
            "Execution time in seconds above which "
            "a pipeline is considered slow"
        ),
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return performance statistics for pipeline runs.

    Includes completed runs, success and failure rates,
    execution-time statistics, and slow pipeline runs.
    """

    runs = get_all_runs(db)

    report = generate_performance_report(
        runs,
        slow_threshold=slow_threshold,
    )

    return report
