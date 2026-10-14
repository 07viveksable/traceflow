MAX_RETRIES = 3


def get_retry_policy(
    fingerprint: str,
    attempt_number: int
):

    fingerprint = fingerprint.upper()

    if fingerprint != "TIMEOUT":
        return {
            "eligible": False,
            "delay_seconds": 0,
            "message": (
                "This failure type is not eligible "
                "for automatic retry."
            )
        }

    if attempt_number < 1:
        return {
            "eligible": False,
            "delay_seconds": 0,
            "message": "Invalid retry attempt number."
        }

    if attempt_number > MAX_RETRIES:
        return {
            "eligible": False,
            "delay_seconds": 0,
            "message": (
                "Maximum retry limit reached."
            )
        }

    delay_seconds = 2 ** attempt_number

    return {
        "eligible": True,
        "delay_seconds": delay_seconds,
        "message": (
            f"Timeout failure is eligible for retry "
            f"{attempt_number} of {MAX_RETRIES}. "
            f"Wait {delay_seconds} seconds before retrying."
        )
    }