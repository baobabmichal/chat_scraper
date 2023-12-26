import os
from time import sleep

from dotenv import load_dotenv
from selenium import webdriver

from packages.chat_scraper.manager.global_manager import GlobalManager, PageStatus

load_dotenv()
MAIN_URL = os.environ["MAIN_URL"]
ROOM = os.environ["ROOM"]
ROOM_URL = os.environ["ROOM_URL"]
USER_LOGIN = os.environ["USER_LOGIN"]
USER_PASSWORD = os.environ["USER_PASSWORD"]


def test_add_and_delete():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    manager = GlobalManager(driver, room_url=ROOM_URL, room_name=ROOM)

    assert manager.page_status == PageStatus.login_page
    manager.check_page_status()

    manager.log_into(USER_LOGIN, USER_PASSWORD)

    assert manager.page_status == PageStatus.room_page
    manager.check_page_status()

    for i in range(1, 8):
        sleep(1)
        manager.room_manager.open_chat_random_registered_user()
        assert manager.room_manager._count_tabs() == i + 1
        sleep(1)

    for i in range(1, 8):
        sleep(1)
        manager.room_manager.close_chat_random_registered_user()
        assert manager.room_manager._count_tabs() == 8 - i
        sleep(1)

    driver.close()


def test_random_moves():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    manager = GlobalManager(driver, room_url=ROOM_URL, room_name=ROOM)

    assert manager.page_status == PageStatus.login_page
    manager.check_page_status()

    manager.log_into(USER_LOGIN, USER_PASSWORD)

    assert manager.page_status == PageStatus.room_page
    manager.check_page_status()

    for _ in range(20):
        manager.save_page_source()
        sleep(1)
        manager.room_manager.random_move()
        sleep(1)

    driver.close()
