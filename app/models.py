from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from app.database import Base


class PipelineRun(Base):

    __tablename__ = "pipeline_runs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    run_id = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    pipeline_name = Column(
        String(200),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )

    records_processed = Column(
        Integer,
        default=0
    )

    start_time = Column(
        DateTime,
        nullable=False
    )

    end_time = Column(
        DateTime,
        nullable=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    error_message = Column(
        String(1000),
        nullable=True
    )