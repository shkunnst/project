from typing import List, Optional
from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from back.database import User, WorkData, UserRole, get_db_session
from back.services.auth import get_current_user

async def get_user_work_data(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> WorkData:
    # Check if user is requesting their own data or is a leader of the same department
    if current_user.id != user_id and current_user.role != UserRole.LEADER:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to view this user's work data"
        )
    
    # If user is a leader, check if target user is in the same department
    if current_user.role == UserRole.LEADER:
        target_user = await session.get(User, user_id)
        if not target_user or target_user.department_id != current_user.department_id:
            raise HTTPException(
                status_code=403,
                detail="You can only view work data of users in your department"
            )
    
    result = await session.execute(
        select(WorkData).where(WorkData.user_id == user_id)
    )
    work_data = result.scalar_one_or_none()
    
    if not work_data:
        raise HTTPException(
            status_code=404,
            detail="Work data not found"
        )
    
    return work_data

async def update_user_work_data(
    user_id: int,
    working_hours: Optional[float] = None,
    bonuses: Optional[float] = None,
    fines: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> WorkData:
    # Only leaders can update work data
    if current_user.role != UserRole.LEADER:
        raise HTTPException(
            status_code=403,
            detail="Only leaders can update work data"
        )
    
    # Check if target user is in the same department
    target_user = await session.get(User, user_id)
    if not target_user or target_user.department_id != current_user.department_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update work data of users in your department"
        )
    
    result = await session.execute(
        select(WorkData).where(WorkData.user_id == user_id)
    )
    work_data = result.scalar_one_or_none()
    
    if not work_data:
        work_data = WorkData(user_id=user_id)
        session.add(work_data)
    
    if working_hours is not None:
        work_data.working_hours = working_hours
    if bonuses is not None:
        work_data.bonuses = bonuses
    if fines is not None:
        work_data.fines = fines
    
    await session.commit()
    await session.refresh(work_data)
    return work_data

async def get_department_work_data(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[WorkData]:
    # Only leaders can view department work data
    if current_user.role != UserRole.LEADER:
        raise HTTPException(
            status_code=403,
            detail="Only leaders can view department work data"
        )
    
    result = await session.execute(
        select(WorkData)
        .join(User)
        .where(User.department_id == current_user.department_id)
    )
    return result.scalars().all() 