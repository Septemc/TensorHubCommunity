from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


settings = get_settings()
engine = create_async_engine(settings.database_url, future=True, echo=settings.debug)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
