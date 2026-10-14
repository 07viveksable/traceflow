from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint
)

from app.database import Base


class RetryAttempt(Base):

    __tablename__ = "retry_attempts"

    __table_args__ = (
        UniqueConstraint(
            "incident_id",
            "attempt_number",
            name="uq_retry_incident_attempt"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    run_id = Column(
        String(100),
        ForeignKey("pipeline_runs.run_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    attempt_number = Column(
        Integer,
        nullable=False
    )

    delay_seconds = Column(
        Integer,
        nullable=False,
        default=0
    )

    status = Column(
        String(50),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )