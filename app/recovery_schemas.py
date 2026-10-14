from datetime import datetime

from pydantic import BaseModel


class RecoveryAttemptResponse(BaseModel):

    id: int

    incident_id: int

    run_id: str

    action: str

    risk_level: str

    status: str

    message: str

    attempt_number: int

    created_at: datetime

    completed_at: datetime | None = None

    class Config:
        from_attributes = True