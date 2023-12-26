import os

from dotenv import load_dotenv
from selenium import webdriver

from packages.chat_scraper.manager.global_manager import GlobalManager, PageStatus

load_dotenv()
MAIN_URL = os.environ["MAIN_URL"]
ROOM = os.environ["ROOM"]
ROOM_URL = os.environ["ROOM_URL"]
USER_LOGIN = os.environ["USER_LOGIN"]
USER_PASSWORD = os.environ["USER_PASSWORD"]


def test_global_manager():
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    manager = GlobalManager(driver, room_url=ROOM_URL, room_name=ROOM)

    assert manager.page_status == PageStatus.login_page
    manager.check_page_status()

    manager.log_into(USER_LOGIN, USER_PASSWORD)

    assert manager.page_status == PageStatus.room_page
    manager.check_page_status()

    manager.save_page_source()
    for i in range(1,8):
        manager.save_page_source()
        manager.room_manager.new_chat_random_registered_user()
        assert manager.room_manager._count_tabs() == i+1

    driver.close()
