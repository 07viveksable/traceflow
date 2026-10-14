from datetime import datetime

from pydantic import BaseModel


class PipelineRunResponse(BaseModel):

    run_id: str

    pipeline_name: str

    status: str

    records_processed: int

    start_time: datetime

    end_time: datetime | None = None

    user_id: int

    error_message: str | None = None

    class Config:
        from_attributes = True