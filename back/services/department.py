from typing import List, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from back.models import Department


async def get_all_departments(session: AsyncSession) -> List[Dict]:
    """
    Retrieve all departments with their IDs and names
    
    Args:
        session: The database session
        
    Returns:
        List of dictionaries containing department information
    """
    # Execute query to get all departments
    result = await session.execute(select(Department))
    departments = result.scalars().all()

    # Convert to list of dictionaries
    department_list = [
        {"id": dept.id, "name": dept.name}
        for dept in departments
    ]

    return department_list
