from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

from packages.common.data_model import Room


def user_login(driver: WebDriver, user_login: str, user_password: str):
    driver.find_element(By.CLASS_NAME, "rodo-popup-agree").click()
    driver.find_element(By.CSS_SELECTOR, '[for="login-user"]').click()
    driver.find_element(By.ID, "nick-login").send_keys(user_login)
    driver.find_element(By.ID, "password-login").send_keys(user_password)
    driver.find_element(By.ID, "enter-login").click()
