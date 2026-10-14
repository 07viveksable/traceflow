
from types import SimpleNamespace

from app.retry_analytics import (
    generate_retry_analytics,
    generate_retry_health_report,
)


def make_attempt(incident_id, attempt_number, status):
    return SimpleNamespace(
        incident_id=incident_id,
        run_id=f"run-{incident_id}",
        attempt_number=attempt_number,
        status=status,
        message="Test retry",
    )


def test_retry_analytics_counts():
    attempts = [
        make_attempt(1, 1, "SUCCESS"),
        make_attempt(2, 1, "FAILED"),
        make_attempt(2, 2, "PENDING"),
    ]

    result = generate_retry_analytics(attempts)

    assert result["total_retries"] == 3
    assert result["successful_retries"] == 1
    assert result["failed_retries"] == 1
    assert result["pending_retries"] == 1


def test_retry_health_detects_recovered_incident():
    attempts = [
        make_attempt(1, 1, "FAILED"),
        make_attempt(1, 2, "SUCCESS"),
    ]

    report = generate_retry_health_report(attempts)

    assert len(report) == 1
    assert report[0]["incident_id"] == 1
    assert report[0]["health"] == "RECOVERED"
