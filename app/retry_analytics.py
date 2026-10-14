
from collections import defaultdict


MAX_RETRIES = 3


def normalize_status(status):
    """Convert a status into a consistent uppercase string."""
    return str(status or "").strip().upper()


def generate_retry_analytics(retry_attempts):
    """Generate overall retry statistics."""

    total_retries = len(retry_attempts)

    successful_retries = 0
    failed_retries = 0
    pending_retries = 0
    other_retries = 0

    for attempt in retry_attempts:
        status = normalize_status(attempt.status)

        if status in {"SUCCESS", "SUCCEEDED", "SIMULATED_SUCCESS"}:
            successful_retries += 1

        elif status in {"FAILED", "ERROR"}:
            failed_retries += 1

        elif status in {
            "PENDING",
            "READY",
            "IN_PROGRESS",
            "WAITING",
            "WAITING_FOR_APPROVAL",
        }:
            pending_retries += 1

        else:
            other_retries += 1

    return {
        "total_retries": total_retries,
        "successful_retries": successful_retries,
        "failed_retries": failed_retries,
        "pending_retries": pending_retries,
        "other_statuses": other_retries,
        "max_retries_per_incident": MAX_RETRIES,
    }


def generate_retry_health_report(retry_attempts):
    """Group retry attempts by incident and identify retry health."""

    incidents = defaultdict(list)

    for attempt in retry_attempts:
        incidents[attempt.incident_id].append(attempt)

    report = []

    for incident_id, attempts in incidents.items():
        attempts.sort(key=lambda item: item.attempt_number)

        latest_attempt = attempts[-1]
        latest_status = normalize_status(latest_attempt.status)
        attempt_count = len(attempts)

        if latest_status in {"SUCCESS", "SUCCEEDED", "SIMULATED_SUCCESS"}:
            health = "RECOVERED"

        elif attempt_count >= MAX_RETRIES:
            health = "RETRY_LIMIT_REACHED"

        elif latest_status in {"FAILED", "ERROR"}:
            health = "RETRY_NEEDED"

        else:
            health = "MONITORING"

        report.append(
            {
                "incident_id": incident_id,
                "run_id": latest_attempt.run_id,
                "total_attempts": attempt_count,
                "latest_attempt_number": latest_attempt.attempt_number,
                "latest_status": latest_attempt.status,
                "health": health,
                "last_message": latest_attempt.message,
            }
        )

    report.sort(key=lambda item: item["incident_id"])

    return report
