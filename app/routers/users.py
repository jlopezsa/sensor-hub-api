from typing import List

from fastapi import APIRouter, Query

from app.schemas.user import User
from app.services.user_service import list_users as svc_list_users, get_user as svc_get_user
from app.utils.common import paginate


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[User])
def list_users(skip: int = Query(0, ge=0), limit: int | None = Query(None, ge=1)):
    return paginate(svc_list_users(), skip=skip, limit=limit)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int):
    return svc_get_user(user_id)

