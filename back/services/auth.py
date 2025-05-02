from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, Response, Cookie, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from back.database import get_db_session, get_db, get_async_db
from back.models import User, UserRole
from back.settings import SECRET_KEY, logger

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def authenticate_user(session: AsyncSession, username: str, password: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


async def create_user(session: AsyncSession, username: str, password: str,
                      recovery_word: str, recovery_hint: str, role: UserRole):
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        password=hashed_password,
        recovery_word=recovery_word,
        recovery_hint=recovery_hint,
        role=role
    )
    session.add(user)
    await session.commit()
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,  # Set to True in production
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # Convert days to seconds
    )


def remove_auth_cookie(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,  # Set to True in production
        samesite="lax"
    )


async def get_current_user(
    access_token: str = Cookie(None, alias="access_token"),
    session: AsyncSession = Depends(get_async_db)  # Change from get_db_session to get_db
) -> User:
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except Exception as e:  # Replace jwt.JWTError with a general Exception
        logger.error(f"Error validating access token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
    
    try:
        # Use the session that was passed as a dependency
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )
        
        return user
    except Exception as e:
        logger.error(f"Database error in get_current_user: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )