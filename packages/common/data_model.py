from pydantic import BaseModel, ConfigDict


class CustomModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Room(CustomModel):
    name: str
    link: str
    people: int
