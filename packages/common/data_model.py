import enum

from pydantic import BaseModel, ConfigDict


class CustomModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PageStatus(enum.Enum):
    main_page = "main_page"
    login_page = "login_page"
    room_page = "room_page"


class TabStatus(enum.Enum):
    visible = "visible"
    at_the_button = "at_the_button"
    hidden = "hidden"
