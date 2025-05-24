"""
Database session dependency with transaction support.
"""

from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import AsyncSessionFactory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get asynchronous database session.

    The session will automatically rollback on exceptions
    and close when done.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Type annotation for dependency
SessionDep = Annotated[AsyncSession, Depends(get_session)]
