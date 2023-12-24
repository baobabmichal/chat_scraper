import os

from dotenv import load_dotenv
from selenium import webdriver

from packages.chat_scraper.main_utils import get_rooms

load_dotenv()
MAIN_URL = os.environ["MAIN_URL"]


def test_get_rooms():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    driver.get(MAIN_URL)
    rooms = get_rooms(driver, max_number=5)

    assert len(rooms) == 5
