from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from back.database import User, UserRole
from back.settings import pwd_context


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def authenticate_user(session: AsyncSession, username: str, password: str):
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def create_user(session: AsyncSession, username: str, password: str, department_id: int,
                      recovery_word: str, recovery_hint: str, role: UserRole):
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        password=hashed_password,
        department_id=department_id,
        recovery_word=recovery_word,
        recovery_hint=recovery_hint,
        role=role
    )
    session.add(user)
    await session.commit()
    return user
