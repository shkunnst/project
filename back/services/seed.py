from sqlalchemy import select

from back.database import async_engine, get_async_db
from back.models import Base
from back.models import User, Department, UserRole
from back.services.auth import get_password_hash


# Create base class for declarative models

async def seed():
    # Create a session using the session factory directly
    async for session in get_async_db():
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


# Function to initialize database
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)