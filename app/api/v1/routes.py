from fastapi import APIRouter

router = APIRouter()


@router.get("/ping", tags=["utils"])
def ping():
    return {"ping": "pong"}


@router.get("/items", tags=["items"])
def list_items():
    return {"items": []}

