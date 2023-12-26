from functools import partial
from itertools import chain
from random import choice

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from packages.chat_scraper.manager.submanagers.inner_id_utils import extract_id

MAX_TABS = 8


class RoomManager:
    def __init__(self, driver: WebDriver, room_name: str) -> None:
        self.driver = driver

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "m-tab-main-container-1-nav")))
        tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav")
        WebDriverWait(tabs_area, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        active_tab = tabs_area.find_element(By.TAG_NAME, "a")
        self.room_id = extract_id(active_tab)
        self.room_name = room_name

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m-usersList-sublist")))
        sublist = self.driver.find_element(By.ID, f"m-users-registered_{self.room_id}")
        WebDriverWait(sublist, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m-list-user-item")))

        self.id2name_mapping: dict[int, str] = {self.room_id: self.room_name}

        self.tabs_visible: list[int] = [self.room_id]
        self.tabs_at_the_button: list[int] = []
        self.tabs_listed: list[int] = []

        self.tab_active: int = self.room_id

    def random_move(self) -> None:
        methods_available = []
        if self._count_tabs() > 1:
            methods_available.append(self.choose_random_tab)
            methods_available.append(self.close_chat_random_registered_user)

        if self._count_tabs() < MAX_TABS:
            methods_available.append(self.open_chat_random_registered_user)

        if self.tab_active != self.room_name:
            methods_available.append(partial(self.send_message, "elo"))

        choice(methods_available)()

    def open_chat_random_registered_user(self) -> None:
        if self._count_tabs() == MAX_TABS:
            raise ValueError("Max number of tabs!")
        if self.tab_active != self.room_name:
            self._choose_room()
        sublist = self.driver.find_element(By.ID, f"m-users-registered_{self.room_id}")
        WebDriverWait(sublist, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m-list-user-item")))
        user_elements = sublist.find_elements(By.CLASS_NAME, "m-list-user-item")
        user_element = choice(user_elements)
        user_element.click()
        self._update_statuses()

    def close_chat_random_registered_user(self) -> None:
        if self._count_tabs() == 1:
            raise ValueError("No chats open!")
        tabs = self._all_tabs()
        tabs.remove(self.room_id)
        user_name = choice(tabs)
        self._close_tab(user_name)
        self._update_statuses()

    def choose_random_tab(self) -> None:
        not_active_tabs = self._all_tabs()
        not_active_tabs.remove(self.tab_active)
        tab_id = choice(not_active_tabs)
        self._choose_tab(tab_id)

    def close_current_tab(self) -> None:
        if self.tab_active == self.room_id:
            raise ValueError("Cannot close room!")
        else:
            self._close_tab(self.tab_active)

    def print_current_tab_info(self) -> None:
        tab_active_name = self.id2name_mapping[self.tab_active]
        title = "=" * 10 + tab_active_name + "=" * 10 + "\n"
        messages = self._get_all_messages()
        print(title + messages)

    def send_message(self, message: str):
        self.driver.find_element(By.ID, f"m-textMessage-{self.tab_active}").send_keys(message)
        self.driver.find_element(By.ID, f"m-sendMessage-button-{self.tab_active}").click()

    def _choose_room(self) -> None:
        self._choose_tab(self.room_id)

    def _choose_tab(self, tab_id: int) -> None:
        if tab_id == self.tab_active:
            return
        if tab_id in self.tabs_at_the_button:
            self._click_more_button()
            self._update_statuses()
            return
        if tab_id in self.tabs_visible:
            self.driver.find_element(By.ID, f"m-a-{tab_id}").click()
            self._update_statuses()
            return
        if tab_id in self.tabs_listed:
            self._click_more_button()
            self.driver.find_element(By.ID, f"m-a-{tab_id}").click()
            self._update_statuses()
        raise ValueError(f"Tab {tab_id} not found!")

    def _close_tab(self, tab_id: int) -> None:
        if tab_id in self.tabs_visible:
            self.driver.find_element(By.ID, f"m-close-{tab_id}").click()
            self._update_statuses()
            return
        elif tab_id in self.tabs_at_the_button:
            self._click_more_button()
            self.driver.find_element(By.ID, f"m-close-{tab_id}").click()
            self._update_statuses()
            return
        elif tab_id in self.tabs_listed:
            self._click_more_button()
            self.driver.find_element(By.ID, f"m-close-{tab_id}").click()
            self._update_statuses()
            return
        raise ValueError(f"Tab {tab_id} not found!")

    def _click_more_button(self) -> None:
        self.driver.find_element(By.ID, "m-more-button").click()

    def _all_tabs(self) -> list[str]:
        return list(chain(self.tabs_visible, self.tabs_at_the_button, self.tabs_listed))

    def _count_tabs(self) -> int:
        return len(self._all_tabs())

    def _get_all_messages(self) -> str:
        message_area = self.driver.find_element(By.ID, f"m-messages_{self.tab_active}")
        return message_area.get_attribute("innerText")

    def _update_statuses(self) -> None:
        tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav")
        tab_elements = tabs_area.find_elements(By.TAG_NAME, "a")
        self.tabs_visible = []
        for element in tab_elements:
            name = element.get_attribute("innerText").upper()
            id = extract_id(element)
            self.tabs_visible.append(id)
            self.id2name_mapping[id] = name
            if element.get_attribute("class") == "active":
                self.tab_active = id

        tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav-listed")
        tab_elements = tabs_area.find_elements(By.TAG_NAME, "a")
        if len(tab_elements) == 1:
            name = tab_elements[0].get_attribute("innerText").upper()
            id = extract_id(element)
            self.tabs_at_the_button = [id]
            self.tabs_listed = []
            self.id2name_mapping[id] = name
        else:
            self.tabs_at_the_button = []
            for element in tab_elements:
                name = element.get_attribute("innerText").upper()
                id = extract_id(element)
                self.tabs_listed.append(id)
                self.id2name_mapping[id] = name
