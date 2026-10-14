from sqlalchemy.orm import Session

from app.user_models import User
from app.roles import Role


def create_user(
    db: Session,
    username: str,
    email: str,
    hashed_password: str
):
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=Role.VIEWER,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_username(
    db: Session,
    username: str
):
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str
):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )