from datetime import datetime

from pydantic import BaseModel


class PipelineLogResponse(BaseModel):

    id: int

    run_id: str

    level: str

    message: str

    timestamp: datetime

    class Config:
        from_attributes = True