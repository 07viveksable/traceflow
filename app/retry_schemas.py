from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RetryAttemptResponse(BaseModel):

    id: int
    incident_id: int
    run_id: str
    attempt_number: int
    delay_seconds: int
    status: str
    message: str
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )   