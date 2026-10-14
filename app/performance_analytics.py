
from statistics import mean


def generate_performance_report(runs, slow_threshold=5.0):
    """
    Generate performance statistics from pipeline run records.

    Args:
        runs: List of PipelineRun database objects.
        slow_threshold: Execution time in seconds above which
                        a successful or failed completed run
                        is considered slow.

    Returns:
        Dictionary containing performance statistics.
    """

    total_runs = len(runs)

    successful_runs = []
    failed_runs = []
    completed_durations = []
    slow_runs = []

    for run in runs:
        status = str(run.status or "").strip().upper()

        if status in {"SUCCESS", "SUCCEEDED"}:
            successful_runs.append(run)

        elif status in {"FAILED", "ERROR"}:
            failed_runs.append(run)

        # Calculate duration only when both timestamps exist.
        if run.start_time and run.end_time:
            duration = (
                run.end_time - run.start_time
            ).total_seconds()

            # Ignore negative durations caused by bad timestamps.
            if duration >= 0:
                completed_durations.append({
                    "run_id": run.run_id,
                    "pipeline_name": run.pipeline_name,
                    "status": status,
                    "execution_time_seconds": round(duration, 3),
                })

                if duration > slow_threshold:
                    slow_runs.append({
                        "run_id": run.run_id,
                        "pipeline_name": run.pipeline_name,
                        "status": status,
                        "execution_time_seconds": round(duration, 3),
                    })

    completed_runs = len(completed_durations)

    average_execution_time = (
        mean(
            item["execution_time_seconds"]
            for item in completed_durations
        )
        if completed_runs
        else 0.0
    )

    execution_times = [
        item["execution_time_seconds"]
        for item in completed_durations
    ]

    success_rate = (
        len(successful_runs) / completed_runs * 100
        if completed_runs
        else 0.0
    )

    failure_rate = (
        len(failed_runs) / completed_runs * 100
        if completed_runs
        else 0.0
    )

    return {
        "total_runs": total_runs,
        "completed_runs": completed_runs,
        "successful_runs": len(successful_runs),
        "failed_runs": len(failed_runs),
        "success_rate_percent": round(success_rate, 2),
        "failure_rate_percent": round(failure_rate, 2),
        "average_execution_time_seconds": round(
            average_execution_time, 3
        ),
        "fastest_execution_time_seconds": (
            min(execution_times) if execution_times else 0.0
        ),
        "slowest_execution_time_seconds": (
            max(execution_times) if execution_times else 0.0
        ),
        "slow_threshold_seconds": slow_threshold,
        "slow_runs_count": len(slow_runs),
        "slow_runs": sorted(
            slow_runs,
            key=lambda item: item["execution_time_seconds"],
            reverse=True,
        ),
        "execution_history": sorted(
            completed_durations,
            key=lambda item: item["execution_time_seconds"],
            reverse=True,
        ),
    }
