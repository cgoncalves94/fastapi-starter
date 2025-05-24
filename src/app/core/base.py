"""
Base repository with common CRUD operations (Async).
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, func, select

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """Get a record by ID or return None if not found."""
        return await self.session.get(self.model, id)

    async def get_multi(self, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get multiple records with pagination."""
        statement = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create(self, *, obj_in: dict[str, Any]) -> ModelType:
        """Create a new record."""
        db_obj = self.model.model_validate(obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, *, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        """Update an existing record."""
        db_obj.sqlmodel_update(obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, *, id: UUID) -> ModelType | None:
        """Delete a record by ID. Returns the deleted object or None if not found."""
        obj = await self.session.get(self.model, id)
        if not obj:
            return None
        await self.session.delete(obj)
        await self.session.flush()
        return obj

    async def count(self) -> int:
        """Count total records efficiently."""
        statement = select(func.count()).select_from(self.model)
        result = await self.session.execute(statement)
        scalar_result = result.scalar_one_or_none()
        return scalar_result if scalar_result is not None else 0
