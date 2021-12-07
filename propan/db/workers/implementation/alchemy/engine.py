import asyncio

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from propan.db.workers.model.connection_params import Connection


class AlchemyAsyncEngine:
    async_session_maker: sessionmaker

    def __init__(self, conn: Connection):
        engine = create_async_engine(
            f"postgresql+asyncpg://{conn.user}:{conn.password}@{conn.host}/{conn.name}",
            echo=False,
        )

        self.async_session_maker = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )


    def get_session(self, func):
        async def wrapped(*args, **kwargs):
            async with self.async_session_maker() as session:
                return await func(*args, session=session, **kwargs)
        return wrapped