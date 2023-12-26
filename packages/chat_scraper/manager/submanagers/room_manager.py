from functools import partial
from itertools import chain
from random import choice

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

MAX_TABS = 8


class RoomManager:
    def __init__(self, driver: WebDriver, room_name: str) -> None:
        self.driver = driver
        self.room_name = room_name

        self.tabs_visible: list[str] = [room_name]
        self.tabs_at_the_button: list[str] = []
        self.tabs_listed: list[str] = []

        self.tab_active: str = room_name

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "m-tab-main-container-1-nav")))
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m-usersList-sublist")))
        sublist = self.driver.find_elements(By.CLASS_NAME, "m-usersList-sublist")[4]
        WebDriverWait(sublist, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m-list-user-item")))

    def random_move(self) -> None:
        if self._count_tabs() == MAX_TABS:
            methods_available = [self.close_chat_random_registered_user, self.choose_random_tab, partial(self.send_message,"elo")]
        elif self._count_tabs() == 1:
            methods_available = [self.open_chat_random_registered_user]
        else:
            methods_available = [
                self.close_chat_random_registered_user,
                self.open_chat_random_registered_user,
                self.choose_random_tab,
                partial(self.send_message,"elo")
            ]
        choice(methods_available)()

    def open_chat_random_registered_user(self) -> None:
        if self._count_tabs() == MAX_TABS:
            raise ValueError("Max number of tabs!")
        if self.tab_active != self.room_name:
            self._choose_room()
        primary_list = self.driver.find_elements(By.CLASS_NAME, "m-user-list-primary")
        sublist = primary_list[-1].find_elements(By.CLASS_NAME, "m-usersList-sublist")[4]
        WebDriverWait(sublist, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m-list-user-item")))
        user_elements = sublist.find_elements(By.CLASS_NAME, "m-list-user-item")
        user_element = choice(user_elements)
        user_element.click()
        self._update_statuses()

    def close_chat_random_registered_user(self) -> None:
        if self._count_tabs() == 1:
            raise ValueError("No chats open!")
        tabs = self._all_tabs()
        tabs.remove(self.room_name)
        user_name = choice(tabs)
        self._close_tab(user_name)
        self._update_statuses()

    def choose_random_tab(self) -> None:
        not_active_tabs = self._all_tabs()
        not_active_tabs.remove(self.tab_active)
        tab_name = choice(not_active_tabs)
        self._choose_tab(tab_name)

    def close_current_tab(self) -> None:
        if self.tab_active == self.room_name:
            raise ValueError("Cannot close room!")
        else:
            self._close_tab(self.tab_active)

    def print_current_tab_info(self) -> None:
        title = "=" * 10 + self.tab_active + "=" * 10 + "\n"
        messages = self._get_all_messages()
        print(title + messages)

    def send_message(self, message: str):
        active_tab_index = self.tabs_visible.index(self.tab_active)
        self.driver.find_elements(By.CLASS_NAME, "text-input")[active_tab_index].send_keys(message)
        self.driver.find_elements(By.CLASS_NAME, "button-send")[active_tab_index].click()

    def _choose_room(self) -> None:
        self._choose_tab(self.room_name)

    def _choose_tab(self, tab_name: str) -> None:
        if tab_name == self.tab_active:
            return
        elif tab_name in self.tabs_at_the_button:
            self._click_more_button()
            self._update_statuses()
            return
        elif tab_name in self.tabs_visible:
            tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav")
            tab_elements = tabs_area.find_elements(By.TAG_NAME, "a")
            for element in tab_elements:
                element_name = element.get_attribute("innerText")
                if element_name == tab_name.upper():
                    element.click()
                    self._update_statuses()
                    return
        elif tab_name in self.tabs_listed:
            self._click_more_button()
            tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav-listed")
            tab_elements = tabs_area.find_elements(By.TAG_NAME, "a")
            for element in tab_elements:
                element_name = element.get_attribute("innerText")
                if element_name == tab_name.upper():
                    element.click()
                    self._update_statuses()
                    return
        raise ValueError("Tab not found!")

    def _close_tab(self, tab_name: str) -> None:
        if tab_name in self.tabs_visible:
            tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav")
            tab_elements = tabs_area.find_elements(By.TAG_NAME, "a")
            for element in tab_elements:
                element_name = element.get_attribute("innerText")
                if element_name == tab_name.upper():
                    close_button = element.find_element(By.CLASS_NAME, "close-room")
                    close_button.click()
                    self._update_statuses()
                    return
            return
        elif tab_name in self.tabs_at_the_button:
            self._click_more_button()
            self._update_statuses()
            self._close_tab(tab_name)
            return
        elif tab_name in self.tabs_listed:
            self._click_more_button()
            tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav-listed")
            tab_elements = tabs_area.find_elements(By.TAG_NAME, "a")
            for element in tab_elements:
                element_name = element.get_attribute("innerText")
                if element_name == tab_name.upper():
                    close_button = element.find_element(By.CLASS_NAME, "close-room")
                    close_button.click()
                    self._update_statuses()
                    return
        raise ValueError(f"Tab {tab_name} not found!")

    def _click_more_button(self) -> None:
        self.driver.find_element(By.ID, "m-more-button").click()

    def _all_tabs(self) -> list[str]:
        return list(chain(self.tabs_visible, self.tabs_at_the_button, self.tabs_listed))

    def _count_tabs(self) -> int:
        return len(self._all_tabs())

    def _get_all_messages(self) -> str:
        text_area = self.driver.find_element(By.CLASS_NAME, "m-messagesTextArea")
        return text_area.get_attribute("innerText")

    def _update_statuses(self) -> None:
        tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav")
        tab_elements = tabs_area.find_elements(By.TAG_NAME, "a")
        self.tabs_visible = []
        for element in tab_elements:
            self.tabs_visible.append(element.get_attribute("innerText").upper())
            if element.get_attribute("class") == "active":
                self.tab_active = element.get_attribute("innerText").upper()

        tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav-listed")
        tab_elements = tabs_area.find_elements(By.TAG_NAME, "a")
        if len(tab_elements) == 1:
            self.tabs_at_the_button = [tab_elements[0].get_attribute("innerText").upper()]
            self.tabs_listed = []
        else:
            self.tabs_at_the_button = []
            self.tabs_listed = [
                element.get_attribute("innerText").upper()
                for element in tab_elements
                if element.get_attribute("innerText") != ""
            ]
