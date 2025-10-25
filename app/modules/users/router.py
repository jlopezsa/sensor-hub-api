from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.users.schemas import User
from app.modules.users.service import get_user as svc_get_user
from app.modules.users.service import list_users as svc_list_users
from app.utils.common import paginate


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[User])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int | None = Query(None, ge=1),
    session: AsyncSession = Depends(get_session),
):
    users = await svc_list_users(session=session)
    return paginate(users, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await svc_get_user(user_id=user_id, session=session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

