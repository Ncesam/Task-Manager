from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio.engine import create_async_engine

from app.backend.settings.settings import env_settings


class DataBaseSessionCreator:
    def __init__(self):
        async_engine = create_async_engine(url=env_settings.POSTGRESQL_URL, pool_pre_ping=True)
        self.maker = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)

    async def __aenter__(self):
        async with self.maker() as session:
            return session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


SessionCreator = DataBaseSessionCreator()
