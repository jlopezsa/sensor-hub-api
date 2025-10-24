from typing import Sequence, List, TypeVar


T = TypeVar("T")


def paginate(items: Sequence[T], skip: int = 0, limit: int | None = None) -> List[T]:
    if limit is None or limit < 0:
        return list(items[skip:])
    return list(items[skip: skip + limit])

