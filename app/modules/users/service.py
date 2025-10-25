from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.model import User as UserModel
from app.modules.users.schemas import User


async def list_users(session: AsyncSession) -> List[User]:
    result = await session.execute(select(UserModel))
    users = result.scalars().all()
    return [User.model_validate(user) for user in users]


async def get_user(user_id: int, session: AsyncSession) -> User | None:
    result = await session.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return None
    return User.model_validate(user)

