from datetime import datetime

from pydantic import BaseModel


class IncidentResponse(BaseModel):

    id: int

    run_id: str

    incident_type: str

    severity: str

    title: str

    description: str

    status: str

    created_at: datetime

    resolved_at: datetime | None = None

    class Config:
        from_attributes = True