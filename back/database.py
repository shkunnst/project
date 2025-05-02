import os
from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from back.models import Base, User, Department, UserRole
from back.services.auth import get_password_hash

# Database URL - using environment variable with fallback
DB_HOST = os.getenv("DB_HOST", "localhost")
DATABASE_URL = f"postgresql+asyncpg://postgres:postgres@{DB_HOST}:5432/freelance_db"
# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)
# postgresql://postgres:postgres@localhost:5432/freelance_db
# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Function to get database session directly (for non-FastAPI usage)
async def get_db_session() -> AsyncSession:
    async with async_session() as session:
        return session

# Function to initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def seed():
    # Create a session using the session factory directly
    async with async_session() as session:
        try:
            # Check if users already exist
            stmt = select(User)
            result = await session.execute(stmt)
            count = len(result.scalars().all())
            
            if count == 0:
                # Create departments
                department1 = Department(name="IT")
                department2 = Department(name="HR")
                session.add_all([department1, department2])
                await session.flush()  # Flush to get department IDs

                # Create users with proper enum values and department_id instead of department
                user1 = User(
                    username="john_doe", 
                    password=get_password_hash("password123"),
                    department_id=department1.id, 
                    recovery_word="recovery1",
                    recovery_hint="hint1",
                    role=UserRole.LEADER  # Use the actual enum value "руководитель"
                )
                user2 = User(
                    username="jane_smith", 
                    password=get_password_hash("secret_password"),
                    department_id=department2.id,
                    recovery_word="recovery2",
                    recovery_hint="hint2",
                    role=UserRole.SUBORDINATE  # Use the actual enum value "подчиненный"
                )
                admin = User(
                    username="admin",
                    password=get_password_hash("admin_password"),
                    department_id=None,
                    recovery_word="recovery3",
                    recovery_hint="hint3",
                    role=UserRole.ADMIN  # Use the actual enum value "администратор"
                )
                session.add_all([user1, user2, admin])
                
                # Commit the changes
                await session.commit()
                print("Database seeded successfully")
        except Exception as e:
            await session.rollback()
            print(f"Error seeding database: {e}")
            raise