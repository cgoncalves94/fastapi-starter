"""
Database session dependency with transaction support.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionFactory


async def get_session() -> AsyncGenerator[AsyncSession]:
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
        # no finally block — AsyncSessionFactory handles closing


# Type annotation for dependency
SessionDep = Annotated[AsyncSession, Depends(get_session)]
