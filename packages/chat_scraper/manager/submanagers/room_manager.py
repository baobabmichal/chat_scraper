import json
import os
from itertools import chain
from pathlib import Path
from random import choice
from typing import Optional, Pattern

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from packages.chat_scraper.manager.submanagers.inner_id_utils import extract_id

MAX_TABS = 8


class RoomManager:
    def __init__(self, driver: WebDriver, room_name: str, data_path: Optional[Path] = None) -> None:
        self.driver = driver
        self.data_path = data_path

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "m-tab-main-container-1-nav")))
        tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav")
        WebDriverWait(tabs_area, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        active_tab = tabs_area.find_element(By.TAG_NAME, "a")
        self.room_id = extract_id(active_tab)
        self.room_name = room_name

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m-usersList-sublist")))
        sublist = self.driver.find_element(By.ID, f"m-users-registered_{self.room_id}")
        WebDriverWait(sublist, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m-list-user-item")))

        self.mapping: dict[int, dict[str, str]] = {self.room_id: {"name": self.room_name}}
        if data_path and os.path.exists(data_path):
            self.load_data()

        self.tabs_visible: list[int] = [self.room_id]
        self.tabs_at_the_button: list[int] = []
        self.tabs_listed: list[int] = []

        self.tab_active: int = self.room_id

        self.tabs_unseen: list[int] = []

        self.pop_up_seen = False

    def print_unseen(self) -> None:
        self.update_unseen()
        for tab_id in self.tabs_unseen:
            if tab_id != self.room_id:
                self.print_tab_info(tab_id)

    def open_chat_random_registered_user(self, search_regex: Pattern[str]) -> None:
        if self._count_tabs() == MAX_TABS:
            raise ValueError("Max number of tabs!")
        if self.tab_active != self.room_name:
            self._choose_room()
        sublist = self.driver.find_element(By.ID, f"m-users-registered_{self.room_id}")
        found_users = [
            user
            for user in sublist.get_attribute("innerText").splitlines()
            if user.upper() not in self._get_seen_names() and bool(search_regex.search(user))
        ]
        if len(found_users) == 0:
            print("No users left")
            return
        else:
            print(f"Found {len(found_users)} users: {found_users}")
        print(f"New users: {len(found_users)}")
        random_user = choice(found_users)
        selected_index = sublist.get_attribute("innerText").splitlines().index(random_user)

        WebDriverWait(sublist, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m-list-user-item")))
        elements = sublist.find_elements(By.CLASS_NAME, "m-list-user-item")
        user_element = elements[selected_index]

        if random_user == user_element.get_attribute("innerText"):
            print(f"Messaging user {random_user}")
            user_element.click()
            self._update_statuses()
        else:
            print("Problem with validation user name!")
            return

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

    def print_tab_info_current(self) -> None:
        self.print_tab_info(self.tab_active)

    def print_tab_info(self, tab_id: id) -> None:
        tab_active_name = self.mapping[tab_id]["name"]
        title = "=" * 10 + tab_active_name + "=" * 10 + "\n"
        message = self._get_last_message(tab_id)
        print(title + message)

    def send_message(self, message: str):
        self.driver.find_element(By.ID, f"m-textMessage-{self.tab_active}").send_keys(message)
        self.driver.find_element(By.ID, f"m-sendMessage-button-{self.tab_active}").click()
        if not self.pop_up_seen and self.tab_active != self.room_id:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "button-yes")))
            self.driver.find_element(By.CLASS_NAME, "button-yes").click()
            self.pop_up_seen = True

    def load_data(self) -> None:
        with open(self.data_path, "rt") as file:
            self.mapping.update(json.load(file))

    def save_data(self) -> None:
        with open(self.data_path, "wt+") as file:
            json.dump(self.mapping, file)

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
        self.mapping[tab_id]["chat"] = self._get_all_messages(tab_id=tab_id)
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

    def _get_all_messages_current(self) -> str:
        return self._get_all_messages(self.tab_active)

    def _get_all_messages(self, tab_id: int) -> str:
        message_area = self.driver.find_element(By.ID, f"m-messages_{tab_id}")
        return message_area.get_attribute("innerText")

    def _get_last_message(self, tab_id: int) -> str:
        message_area = self.driver.find_element(By.ID, f"m-messages_{tab_id}")
        last_message = message_area.find_elements(By.CLASS_NAME, "m-msg-item")[-1]
        return last_message.get_attribute("innerText")

    def _purge_all(self) -> None:
        for tab_id in [tab for tab in self._all_tabs() if tab != self.room_id]:
            self._purge_tab(tab_id)

    def _purge_tab(self, tab_id: int) -> None:
        message_area = self.driver.find_element(By.ID, f"m-messages_{tab_id}")
        last_message = message_area.find_elements(By.CLASS_NAME, "m-msg-item")[-1]
        system_messages = last_message.find_elements(By.CLASS_NAME, "m-msg-item-system")
        if len(system_messages) > 0:
            last_message = system_messages[0].get_attribute("innerText")
            if "wysyła Ci zdjęcie" not in last_message:
                tab_name = self.mapping[tab_id]["name"]
                print(f"Purging tab {tab_name}. Last system message:{last_message}")
                print(f"Last message: {self._get_last_message(tab_id)}")
                print(f"All messages: {self._get_all_messages(tab_id)}")
                self._close_tab(tab_id)

    def _update_statuses(self) -> None:
        self.tabs_visible = []
        self.tabs_at_the_button = []
        self.tabs_listed = []
        tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav")
        tab_elements = tabs_area.find_elements(By.TAG_NAME, "a")
        for element in tab_elements:
            name = element.get_attribute("innerText").upper()
            id = extract_id(element)
            self.tabs_visible.append(id)
            self._add_to_mapping(id, name)
            if element.get_attribute("class") == "active":
                self.tab_active = id

        tabs_area = self.driver.find_element(By.ID, "m-tab-main-container-1-nav-listed")
        tab_elements = tabs_area.find_elements(By.TAG_NAME, "a")
        if len(tab_elements) == 1:
            element = tab_elements[0]
            name = element.get_attribute("innerText").upper()
            id = extract_id(element)
            self.tabs_at_the_button = [id]
            self.tabs_listed = []
            self._add_to_mapping(id, name)
        else:
            for element in tab_elements:
                name = element.get_attribute("innerText").upper()
                id = extract_id(element)
                self.tabs_listed.append(id)
                self._add_to_mapping(id, name)

    def update_unseen(self) -> None:
        elements = self.driver.find_elements(By.CLASS_NAME, "unseen")
        self.tabs_unseen = [extract_id(element) for element in elements]

    def _get_seen_names(self) -> set[str]:
        return {data["name"] for data in self.mapping.values()}

    def _add_to_mapping(self, id: int, name: str) -> None:
        if id not in self.mapping:
            self.mapping[id] = {"name": name}
