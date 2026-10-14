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


class Incident(Base):

    __tablename__ = "incidents"

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

    incident_type = Column(
        String(100),
        nullable=False
    )

    severity = Column(
        String(20),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="OPEN"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now
    )

    resolved_at = Column(
        DateTime,
        nullable=True
    )