from typing import Optional

from pydantic import BaseModel, ConfigDict
from selenium.webdriver.remote.webelement import WebElement


class CustomModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


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


class Tab(CustomModel):
    tab_name: str
    tab_class: str
    tab_visibility: bool
    web_element: Optional[WebElement]
    close_element: Optional[WebElement]
