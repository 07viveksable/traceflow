from datetime import datetime

from pydantic import BaseModel


class RootCauseAnalysisResponse(BaseModel):

    id: int

    incident_id: int

    run_id: str

    fingerprint: str

    root_cause: str

    suggested_action: str

    confidence: float

    created_at: datetime

    class Config:
        from_attributes = True