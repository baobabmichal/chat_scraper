import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from packages.chat_scraper.manager.global_manager import GlobalManager, PageStatus

load_dotenv()
MAIN_URL = os.environ["MAIN_URL"]
ROOM = os.environ["ROOM"]
USER_LOGIN = os.environ["USER_LOGIN"]
USER_PASSWORD = os.environ["USER_PASSWORD"]


def test_global_manager():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(MAIN_URL)

    manager = GlobalManager(driver)
    assert manager.page_status == PageStatus.main_page
    manager.check_page_status()

    manager.get_into_room(ROOM)

    assert manager.page_status == PageStatus.login_page
    manager.check_page_status()
    
    manager.log_into(USER_LOGIN, USER_PASSWORD)

    assert manager.page_status == PageStatus.room_page
    manager.check_page_status()
