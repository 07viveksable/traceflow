from datetime import datetime

from pydantic import BaseModel


class PipelineMetricResponse(BaseModel):

    id: int

    run_id: str

    execution_time: float

    records_processed: int

    records_failed: int

    status: str

    created_at: datetime

    class Config:
        from_attributes = True