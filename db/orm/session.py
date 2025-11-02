from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from untils.config import DB_PATH, ECHO_BOOL

db_url = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(db_url, echo=ECHO_BOOL)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)