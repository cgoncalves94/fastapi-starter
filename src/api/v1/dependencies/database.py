"""
Database dependency for FastAPI.
"""

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session

# Database session dependency
SessionDep = Annotated[Session, Depends(get_session)]
