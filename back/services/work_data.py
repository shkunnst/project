from typing import List, Optional, Dict
from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from back.database import get_db_session
from back.models import User, UserRole, WorkData
from back.schemas import WorkDataResponse
from back.services.auth import get_current_user

async def get_user_work_data(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict:
    # Check if user is requesting their own data or is a leader of the same department
    if current_user.id != user_id and current_user.role != UserRole.LEADER:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to view this user's work data"
        )
    
    # If user is a leader, check if target user is in the same department
    target_user = await session.get(User, user_id)
    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
        
    if current_user.role == UserRole.LEADER and target_user.department_id != current_user.department_id:
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
    
    # Return dictionary with work data and username
    return {
        "user_id": work_data.user_id,
        "username": target_user.username,
        "working_hours": work_data.working_hours,
        "bonuses": work_data.bonuses,
        "fines": work_data.fines
    }

async def update_user_work_data(
    user_id: int,
    working_hours: Optional[float] = None,
    bonuses: Optional[float] = None,
    fines: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> Dict:
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
    
    # Return dictionary with work data and username
    return {
        "user_id": work_data.user_id,
        "username": target_user.username,
        "working_hours": work_data.working_hours,
        "bonuses": work_data.bonuses,
        "fines": work_data.fines
    }

async def get_department_work_data(
    current_user: User,
    session: AsyncSession
) -> List[Dict]:
    # First, get all users in the department
    users_result = await session.execute(
        select(User).where(User.department_id == current_user.department_id)
    )
    department_users = users_result.scalars().all()
    
    # Create a dictionary of users by id for quick lookup
    users_by_id = {user.id: user for user in department_users}
    
    # Get existing work data for the department
    work_data_result = await session.execute(
        select(WorkData)
        .join(User)
        .where(User.department_id == current_user.department_id)
    )
    existing_work_data = work_data_result.scalars().all()
    
    # Create a dictionary of existing work data by user_id for quick lookup
    work_data_by_user_id = {wd.user_id: wd for wd in existing_work_data}
    
    # Create work data for users who don't have it
    for user in department_users:
        if user.id not in work_data_by_user_id:
            new_work_data = WorkData(
                user_id=user.id,
                working_hours=0,
                bonuses=0,
                fines=0
            )
            session.add(new_work_data)
            work_data_by_user_id[user.id] = new_work_data
    
    # Commit the changes if new work data was created
    if len(work_data_by_user_id) > len(existing_work_data):
        await session.commit()
        
        # Refresh the work data to get the latest values
        for work_data in work_data_by_user_id.values():
            await session.refresh(work_data)
    
    # Create a list of dictionaries with work data and username
    result = []
    for user_id, work_data in work_data_by_user_id.items():
        user = users_by_id.get(user_id)
        if user:
            result.append({
                "user_id": work_data.user_id,
                "username": user.username,
                "working_hours": work_data.working_hours,
                "bonuses": work_data.bonuses,
                "fines": work_data.fines
            })
    
    return result