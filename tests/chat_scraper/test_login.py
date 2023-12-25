import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from packages.chat_scraper.login_utils import log_as_user

load_dotenv()
ROOM_URL = os.environ["ROOM_URL"]
USER_LOGIN = os.environ["USER_LOGIN"]
USER_PASSWORD = os.environ["USER_PASSWORD"]


def test_log_as_user():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    driver.get(ROOM_URL)

    log_as_user(driver, USER_LOGIN, USER_PASSWORD)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m-messagesTextArea")))
    except TimeoutException as e:
        raise(e)
