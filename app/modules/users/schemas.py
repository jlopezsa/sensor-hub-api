from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)

