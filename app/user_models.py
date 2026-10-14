from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean

from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    email = Column(
        String(200),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password = Column(
        String(500),
        nullable=False
    )

    role = Column(
        String(50),
        default="VIEWER",
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    pipeline_runs = relationship(
        "PipelineRun",
        backref="user"
    )