from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from loguru import logger

from .config import config
from .models import Base


engine = create_async_engine(
    config.db.async_url,
    poolclass=NullPool,
    echo=False,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    logger.info("🗄️ Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database initialized successfully")


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
