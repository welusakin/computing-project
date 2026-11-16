"""Engine and session setup. One scoped session per app instance."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def make_session(database_url: str):
    kwargs = {}
    if database_url.endswith(":memory:"):
        # Keep a single connection so the in-memory database survives.
        kwargs = {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
    engine = create_engine(database_url, **kwargs)
    import models  # noqa: F401  (registers tables on Base.metadata)

    Base.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
