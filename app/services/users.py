from sqlalchemy.orm import Session

from app.models.user import User


def list_users(search: str | None, is_active: bool | None, db: Session) -> list[User]:
    query = db.query(User)

    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%"))
            | (User.email.ilike(f"%{search}%"))
        )

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.all()
