import os
import re
from functools import partial
from random import choice
from time import sleep

from dotenv import load_dotenv
from selenium import webdriver

from packages.chat_scraper.manager.global_manager import GlobalManager, PageStatus
from packages.chat_scraper.manager.submanagers.room_manager import MAX_TABS, RoomManager

load_dotenv()
MAIN_URL = os.environ["MAIN_URL"]
ROOM = os.environ["ROOM"]
ROOM_URL = os.environ["ROOM_URL"]
USER_LOGIN = os.environ["USER_LOGIN"]
USER_PASSWORD = os.environ["USER_PASSWORD"]

REGEX = os.environ["REGEX"]
PATTERN = re.compile(REGEX)

MESSAGE = os.environ["MESSAGE"]
DATA_PATH = os.environ["DATA_PATH"]


def random_move(room_manager: RoomManager) -> None:
    methods_available = []
    if room_manager._count_tabs() > 1:
        methods_available.append(room_manager.choose_random_tab)
        methods_available.append(room_manager.close_chat_random_registered_user)

    if room_manager._count_tabs() < MAX_TABS:
        methods_available.append(partial(room_manager.open_chat_random_registered_user, PATTERN))

    if room_manager.tab_active != room_manager.room_id:
        methods_available.append(partial(room_manager.send_message, MESSAGE))

    choice(methods_available)()


def test_add_and_delete():
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    manager = GlobalManager(driver, room_url=ROOM_URL, room_name=ROOM, data_path=DATA_PATH)

    assert manager.page_status == PageStatus.login_page
    manager.check_page_status()

    manager.log_into(USER_LOGIN, USER_PASSWORD)

    assert manager.page_status == PageStatus.room_page
    manager.check_page_status()

    for i in range(1, 8):
        sleep(1)
        manager.room_manager.open_chat_random_registered_user(PATTERN)
        assert manager.room_manager._count_tabs() == i + 1
        sleep(1)

    for i in range(1, 8):
        sleep(1)
        manager.room_manager.close_chat_random_registered_user()
        assert manager.room_manager._count_tabs() == 8 - i
        sleep(1)

    manager.room_manager.save_data()
    driver.close()


def test_random_moves():
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    manager = GlobalManager(driver, room_url=ROOM_URL, room_name=ROOM, data_path=DATA_PATH)

    assert manager.page_status == PageStatus.login_page
    manager.check_page_status()

    manager.log_into(USER_LOGIN, USER_PASSWORD)

    assert manager.page_status == PageStatus.room_page
    manager.check_page_status()

    for _ in range(20):
        manager.save_page_source()
        sleep(1)
        random_move(manager.room_manager)
        sleep(1)

    manager.room_manager.save_data()
    driver.close()
