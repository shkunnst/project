from typing import List, Optional, Dict

from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from back.models import User, UserRole, WorkData, Department
from back.services.auth import get_current_user


async def get_user_work_data(
        user_id: int,
        session: AsyncSession,
    current_user: User = Depends(get_current_user),
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
        session: AsyncSession,
        current_user: User,
        working_hours: Optional[float] = None,
        bonuses: Optional[float] = None,
        fines: Optional[float] = None,
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


async def get_all_users_work_data(
        current_user: User,
        session: AsyncSession
) -> List[Dict]:
    # Only admins can access all users' data
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access all users' data"
        )

    # Get all users
    users_result = await session.execute(select(User))
    all_users = users_result.scalars().all()

    # Create a dictionary of users by id for quick lookup
    users_by_id = {user.id: user for user in all_users}

    # Get all work data
    work_data_result = await session.execute(select(WorkData))
    existing_work_data = work_data_result.scalars().all()

    # Create a dictionary of existing work data by user_id for quick lookup
    work_data_by_user_id = {wd.user_id: wd for wd in existing_work_data}

    # Get all departments for lookup
    departments_result = await session.execute(select(Department))
    departments = {dept.id: dept.name for dept in departments_result.scalars().all()}

    # Create work data for users who don't have it
    for user in all_users:
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

    # Create a list of dictionaries with work data, username, role, and department
    result = []
    for user_id, work_data in work_data_by_user_id.items():
        user = users_by_id.get(user_id)
        if user:
            result.append({
                "user_id": work_data.user_id,
                "username": user.username,
                "role": user.role,
                "department_id": user.department_id,
                "department_name": departments.get(user.department_id),
                "working_hours": work_data.working_hours,
                "bonuses": work_data.bonuses,
                "fines": work_data.fines
            })

    return result


async def update_user_admin_data(
        user_id: int,
        session: AsyncSession,
        current_user: User,
        role: Optional[UserRole] = None,
        department_id: Optional[int] = None,
        working_hours: Optional[float] = None,
        bonuses: Optional[float] = None,
        fines: Optional[float] = None,
) -> Dict:
    # Only admins can update user admin data
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can update user administrative data"
        )

    # Get the target user
    target_user = await session.get(User, user_id)
    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Update user role and department if provided
    if role is not None:
        target_user.role = role
    
    if department_id is not None:
        # Verify department exists
        department = await session.get(Department, department_id)
        if not department and department_id is not None:
            raise HTTPException(
                status_code=404,
                detail="Department not found"
            )
        target_user.department_id = department_id

    # Get or create work data
    result = await session.execute(
        select(WorkData).where(WorkData.user_id == user_id)
    )
    work_data = result.scalar_one_or_none()

    if not work_data:
        work_data = WorkData(user_id=user_id)
        session.add(work_data)

    # Update work data if provided
    if working_hours is not None:
        work_data.working_hours = working_hours
    if bonuses is not None:
        work_data.bonuses = bonuses
    if fines is not None:
        work_data.fines = fines

    # Get department name for response
    department_name = None
    if target_user.department_id:
        dept_result = await session.execute(
            select(Department.name).where(Department.id == target_user.department_id)
        )
        department_name = dept_result.scalar_one_or_none()

    await session.commit()
    await session.refresh(target_user)
    await session.refresh(work_data)

    # Return dictionary with updated user and work data
    return {
        "user_id": target_user.id,
        "username": target_user.username,
        "role": target_user.role,
        "department_id": target_user.department_id,
        "department_name": department_name,
        "working_hours": work_data.working_hours,
        "bonuses": work_data.bonuses,
        "fines": work_data.fines
    }
