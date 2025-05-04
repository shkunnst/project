import os
from typing import AsyncGenerator, Generator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from back.settings import DATABASE_URL
from fastapi import Depends


engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=10,
    pool_recycle=3600,
    pool_pre_ping=True
)

async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=30,
    pool_timeout=10,
    pool_recycle=3600,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()

# Dependency for FastAPI

def get_db() -> Generator[Session, None, None]:
    """Synchronous database session generator with improved error handling"""
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Commit if no exceptions occur
    except Exception as exc:
        db.rollback()  # Rollback on any exception
        raise exc  # Re-raise the exception after rollback
    finally:
        db.close()  # Always close the session

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Корректный генератор сессии"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

