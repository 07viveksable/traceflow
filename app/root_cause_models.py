from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text
)

from app.database import Base


class RootCauseAnalysis(Base):

    __tablename__ = "root_cause_analysis"

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

    fingerprint = Column(
        String(100),
        nullable=False
    )

    root_cause = Column(
        String(255),
        nullable=False
    )

    suggested_action = Column(
        Text,
        nullable=False
    )

    confidence = Column(
        Float,
        nullable=False,
        default=1.0
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now
    )