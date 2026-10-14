from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text
)

from datetime import datetime

from app.database import Base


class PipelineLog(Base):

    __tablename__ = "pipeline_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    run_id = Column(
        String(100),
        ForeignKey("pipeline_runs.run_id"),
        nullable=False,
        index=True
    )

    level = Column(
        String(20),
        nullable=False,
        default="INFO"
    )

    message = Column(
        Text,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.now
    )