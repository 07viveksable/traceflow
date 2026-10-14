
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from app.performance_analytics import generate_performance_report


def create_run(run_id, status, duration=None):
    """Create a fake pipeline run for testing."""

    start_time = datetime(2026, 10, 14, 10, 0, 0)

    end_time = (
        start_time + timedelta(seconds=duration)
        if duration is not None
        else None
    )

    return SimpleNamespace(
        run_id=run_id,
        pipeline_name="Test Pipeline",
        status=status,
        start_time=start_time,
        end_time=end_time,
    )


def test_empty_pipeline_runs():
    """An empty list should return zero performance statistics."""

    report = generate_performance_report([])

    assert report["total_runs"] == 0
    assert report["completed_runs"] == 0
    assert report["successful_runs"] == 0
    assert report["failed_runs"] == 0
    assert report["average_execution_time_seconds"] == 0.0
    assert report["slow_runs_count"] == 0


def test_total_successful_and_failed_runs():
    """Check the counts for successful and failed runs."""

    runs = [
        create_run("run-1", "SUCCESS", 10),
        create_run("run-2", "FAILED", 2),
        create_run("run-3", "SUCCESS", 4),
    ]

    report = generate_performance_report(runs)

    assert report["total_runs"] == 3
    assert report["completed_runs"] == 3
    assert report["successful_runs"] == 2
    assert report["failed_runs"] == 1


def test_execution_time_statistics():
    """Check average, fastest, and slowest execution times."""

    runs = [
        create_run("run-1", "SUCCESS", 10),
        create_run("run-2", "FAILED", 2),
        create_run("run-3", "SUCCESS", 4),
    ]

    report = generate_performance_report(runs)

    assert report["average_execution_time_seconds"] == 5.333
    assert report["fastest_execution_time_seconds"] == 2
    assert report["slowest_execution_time_seconds"] == 10


def test_slow_run_detection():
    """Only runs above the threshold should be classified as slow."""

    runs = [
        create_run("run-1", "SUCCESS", 10),
        create_run("run-2", "SUCCESS", 2),
        create_run("run-3", "FAILED", 7),
    ]

    report = generate_performance_report(
        runs,
        slow_threshold=5,
    )

    assert report["slow_runs_count"] == 2

    slow_run_ids = {
        run["run_id"] for run in report["slow_runs"]
    }

    assert slow_run_ids == {"run-1", "run-3"}


def test_slow_runs_are_sorted_by_duration():
    """The slowest run should appear first."""

    runs = [
        create_run("run-1", "SUCCESS", 8),
        create_run("run-2", "FAILED", 15),
        create_run("run-3", "SUCCESS", 10),
    ]

    report = generate_performance_report(
        runs,
        slow_threshold=5,
    )

    durations = [
        run["execution_time_seconds"]
        for run in report["slow_runs"]
    ]

    assert durations == sorted(durations, reverse=True)


def test_incomplete_run_is_not_completed():
    """A run without an end time should not count as completed."""

    runs = [
        create_run("run-1", "SUCCESS", 5),
        create_run("run-2", "FAILED", None),
    ]

    report = generate_performance_report(runs)

    assert report["total_runs"] == 2
    assert report["completed_runs"] == 1


def test_custom_slow_threshold():
    """The caller should be able to change the slow threshold."""

    runs = [
        create_run("run-1", "SUCCESS", 4),
        create_run("run-2", "SUCCESS", 8),
    ]

    report = generate_performance_report(
        runs,
        slow_threshold=6,
    )

    assert report["slow_threshold_seconds"] == 6
    assert report["slow_runs_count"] == 1
    assert report["slow_runs"][0]["run_id"] == "run-2"


def test_success_and_failure_rates():
    """Rates should be calculated from completed pipeline runs."""

    runs = [
        create_run("run-1", "SUCCESS", 3),
        create_run("run-2", "SUCCESS", 4),
        create_run("run-3", "FAILED", 5),
        create_run("run-4", "FAILED", 6),
    ]

    report = generate_performance_report(runs)

    assert report["success_rate_percent"] == 50.0
    assert report["failure_rate_percent"] == 50.0
