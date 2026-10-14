from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey
)

from datetime import datetime

from app.database import Base


class PipelineMetric(Base):

    __tablename__ = "pipeline_metrics"

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

    execution_time = Column(
        Float,
        nullable=False
    )

    records_processed = Column(
        Integer,
        nullable=False,
        default=0
    )

    records_failed = Column(
        Integer,
        nullable=False,
        default=0
    )

    status = Column(
        String(50),
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now
    )