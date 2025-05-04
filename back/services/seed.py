import json
import os

from dotenv import load_dotenv
from sqlalchemy import select

from back.database import async_engine, get_async_db
from back.models import Base
from back.models import User, Department, UserRole
from back.services.auth import get_password_hash

# Load environment variables
load_dotenv()


def get_admin_credentials():
    """Get admin credentials from environment variables"""
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin_password")
    return admin_username, admin_password


def load_users_from_json():
    """Load regular users data from JSON file"""
    json_path = os.path.join(os.path.dirname(__file__), "../data/users.json")
    try:
        with open(json_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Warning: users.json file not found at {json_path}, using default users")
        # Return default users if file not found
        return {
            "departments": [
                {"name": "IT"},
                {"name": "HR"}
            ],
            "users": [
                {
                    "username": "john_doe",
                    "password": "password123",
                    "department": "IT",
                    "recovery_word": "recovery1",
                    "recovery_hint": "hint1",
                    "role": "LEADER"
                },
                {
                    "username": "jane_smith",
                    "password": "secret_password",
                    "department": "HR",
                    "recovery_word": "recovery2",
                    "recovery_hint": "hint2",
                    "role": "SUBORDINATE"
                }
            ]
        }


async def seed():
    # Create a session using the session factory directly
    async for session in get_async_db():
        try:
            # Check if users already exist
            stmt = select(User)
            result = await session.execute(stmt)
            count = len(result.scalars().all())

            if count == 0:
                # Get admin credentials from environment variables
                admin_username, admin_password = get_admin_credentials()

                # Load user data from JSON
                user_data = load_users_from_json()

                # Create departments
                departments = {}
                for dept_info in user_data.get("departments", []):
                    department = Department(name=dept_info["name"])
                    session.add(department)
                    departments[dept_info["name"]] = department

                await session.flush()  # Flush to get department IDs

                # Create regular users from JSON data
                users = []
                for user_info in user_data.get("users", []):
                    department_name = user_info.get("department")
                    department_id = departments.get(department_name).id if department_name in departments else None

                    role_str = user_info.get("role", "SUBORDINATE")
                    role = getattr(UserRole, role_str)

                    user = User(
                        username=user_info["username"],
                        password=get_password_hash(user_info["password"]),
                        department_id=department_id,
                        recovery_word=user_info["recovery_word"],
                        recovery_hint=user_info["recovery_hint"],
                        role=role
                    )
                    users.append(user)

                # Create admin user from environment variables
                admin = User(
                    username=admin_username,
                    password=get_password_hash(admin_password),
                    department_id=None,
                    recovery_word="admin_recovery",
                    recovery_hint="admin_hint",
                    role=UserRole.ADMIN
                )
                users.append(admin)

                session.add_all(users)

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
