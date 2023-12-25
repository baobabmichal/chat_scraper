from random import choice

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

from packages.common.data_model import MainMessage, Tab, User


class MessageUpdater:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.messages: list[MainMessage] = []

    def update(self):
        if not self.messages:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m-messagesTextArea")))
        text_area = self.driver.find_element(By.CLASS_NAME, "m-messagesTextArea")
        message_elements = text_area.find_elements(By.CLASS_NAME, "m-msg-item-user-message")
        new_message_elements = message_elements[len(self.messages) :]
        print(f"New messages: {len(new_message_elements)}")
        for element in tqdm(new_message_elements):
            user_name, message = element.get_attribute("innerText").split(":", maxsplit=1)
            self.messages.append(MainMessage(user_name=user_name, message=message))


class UserUpdater:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.users: list[User] = []
        self.user_names: set[str] = set()

    def update(self):
        if not self.users:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m-usersList-sublist")))
        user_sublists = self.driver.find_elements(By.CLASS_NAME, "m-usersList-sublist")
        for sublist in user_sublists:
            user_type = sublist.get_attribute("id")
            user_elements = sublist.find_elements(By.CLASS_NAME, "m-list-user-item")
            for user_element in user_elements:
                try:
                    user_name = user_element.get_attribute("innerText")
                except Exception:
                    continue
                if user_name in self.user_names:
                    continue
                print(user_name)
                self.user_names.add(user_name)
                self.users.append(User(user_name=user_name, user_type=user_type, web_element=user_element))

    def click_random_user(self):
        choice([user.web_element for user in self.users]).click()

class TabManager:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.tabs: list[Tab] = []

    def update(self):
        if not self.tabs:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "m-tab-main-container-1-nav")))
        self.tabs = []
        tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav")
        tab_elements = tabs_area.find_elements(By.TAG_NAME, "li")
        for element in tab_elements:
            tab_name = element.get_attribute("innerText")
            tab_class = element.get_attribute("class")
            close_elements = element.find_elements(By.CLASS_NAME, "close-room")
            if len(close_elements) > 0:
                self.tabs.append(Tab(tab_name=tab_name, tab_class=tab_class, web_element=element, tab_visibility=True, close_element=close_elements[0]))
            else:
                self.tabs.append(Tab(tab_name=tab_name, tab_class=tab_class, web_element=element, tab_visibility=True, close_element=None))
        tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav-listed")
        tab_elements = tabs_area.find_elements(By.TAG_NAME, "li")
        for element in tab_elements:
            tab_name = element.get_attribute("innerText")
            tab_class = element.get_attribute("class")
            self.tabs.append(Tab(tab_name=tab_name, tab_class=tab_class, web_element=element, tab_visibility=False, close_element=None))


def send_main_message(driver: WebDriver, message: str):
    driver.find_element(By.CLASS_NAME, "text-input").send_keys(message)
    driver.find_element(By.CLASS_NAME, "button-send").click()
