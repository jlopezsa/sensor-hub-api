from typing import List

from app.modules.users.schemas import User


def list_users() -> List[User]:
    return [User(id=1, name="user-1"), User(id=2, name="user-2")]


def get_user(user_id: int) -> User:
    return User(id=user_id, name=f"user-{user_id}")

