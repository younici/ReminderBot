import os.path

from db.orm.base import Base
from db.orm.session import engine

from untils.config import DB_PATH

async def init_db():
    dir_name = os.path.dirname(DB_PATH)

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)