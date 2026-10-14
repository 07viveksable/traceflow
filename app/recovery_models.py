from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text
)

from app.database import Base


class RecoveryAttempt(Base):

    __tablename__ = "recovery_attempts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=False,
        index=True
    )

    run_id = Column(
        String(100),
        nullable=False,
        index=True
    )

    action = Column(
        String(100),
        nullable=False
    )

    risk_level = Column(
        String(20),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    attempt_number = Column(
        Integer,
        nullable=False,
        default=1
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