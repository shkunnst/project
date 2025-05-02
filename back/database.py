from sqlalchemy import Column, Integer, String, ForeignKey, Enum, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, relationship
import enum
from typing import AsyncGenerator
from fastapi import Depends
import os

# Create base class for declarative models
Base = declarative_base()

# Define role enum
class UserRole(str, enum.Enum):
    LEADER = "руководитель"
    SUBORDINATE = "подчиненный"
    ADMIN = "администратор"

# Department model
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    # Relationship with users
    users = relationship("User", back_populates="department")

# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    recovery_word = Column(String)
    recovery_hint = Column(String)
    role = Column(Enum(UserRole))

    # Foreign key to department
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department = relationship("Department", back_populates="users")

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
                    password="password123", 
                    department_id=department1.id, 
                    recovery_word="recovery1",
                    recovery_hint="hint1",
                    role=UserRole.LEADER  # Use the actual enum value "руководитель"
                )
                user2 = User(
                    username="jane_smith", 
                    password="secret_password", 
                    department_id=department2.id,
                    recovery_word="recovery2",
                    recovery_hint="hint2",
                    role=UserRole.SUBORDINATE  # Use the actual enum value "подчиненный"
                )
                admin = User(
                    username="admin",
                    password="admin_password",
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