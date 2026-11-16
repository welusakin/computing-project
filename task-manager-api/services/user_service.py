"""Business rules for users. No Flask imports in this layer."""
from sqlalchemy import select

from errors import NotFoundError, ValidationError
from models import User

ALLOWED_NOTIFICATION_PREFS = ("email", "sms", "none")


def _clean_notification_pref(value) -> str:
    if not isinstance(value, str) or value not in ALLOWED_NOTIFICATION_PREFS:
        raise ValidationError(
            "notification_pref must be one of: " + ", ".join(ALLOWED_NOTIFICATION_PREFS),
            field="notification_pref",
        )
    return value


def create_user(session, data: dict) -> User:
    name = data.get("name")
    email = data.get("email")
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("name must be a non-empty string", field="name")
    if not isinstance(email, str) or "@" not in email:
        raise ValidationError("email must be a valid address", field="email")
    email = email.strip().lower()
    if session.scalar(select(User).where(User.email == email)) is not None:
        raise ValidationError("email is already registered", field="email")
    user = User(name=name.strip(), email=email)
    session.add(user)
    session.commit()
    return user


def list_users(session) -> list[User]:
    return list(session.scalars(select(User).order_by(User.id)))


def get_user(session, user_id: int) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise NotFoundError("user", user_id)
    return user


def get_notification_pref(session, user_id: int) -> str:
    user = get_user(session, user_id)
    if user.notification_pref is None:
        return "none"
    return user.notification_pref


def set_notification_pref(session, user_id: int, value) -> User:
    user = get_user(session, user_id)
    user.notification_pref = _clean_notification_pref(value)
    session.commit()
    return user
