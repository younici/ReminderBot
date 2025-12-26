import os.path

from sqlalchemy import inspect, text

from db.orm.base import Base
from db.orm.session import engine

from untils.config import DB_PATH


def _apply_migrations(connection):
    """Lightweight migrations to keep SQLite schema in sync."""
    inspector = inspect(connection)
    columns = {col["name"] for col in inspector.get_columns("users")}

    if "premium_until" not in columns:
        dialect = connection.dialect.name
        column_type = "TIMESTAMP"
        if dialect != "sqlite":
            column_type = "TIMESTAMP WITH TIME ZONE"

        connection.execute(
            text(f"ALTER TABLE users ADD COLUMN premium_until {column_type}")
        )


async def init_db():
    dir_name = os.path.dirname(DB_PATH)

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_apply_migrations)
