import enum
from typing import Optional

from pydantic import BaseModel, ConfigDict
from selenium.webdriver.remote.webelement import WebElement


class CustomModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class PageStatus(enum.Enum):
    main_page = "main_page"
    login_page = "login_page"
    room_page = "room_page"


class TabStatus(enum.Enum):
    visible = "visible"
    at_the_button = "at_the_button"
    hidden = "hidden"


class Room(CustomModel):
    name: str
    link: str
    people: int


class MainMessage(CustomModel):
    user_name: str
    message: str


class User(CustomModel):
    user_name: str
    user_type: str
    web_element: Optional[WebElement]
