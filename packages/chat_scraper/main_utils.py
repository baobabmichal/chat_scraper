from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

from packages.common.data_model import Room


def get_rooms(driver: WebDriver, max_number: Optional[int] = None) -> list[Room]:
    room_elements = get_elements_by_class(driver, "room-item", max_number)
    results = []

    seen = set()
    for element in tqdm(room_elements):
        name = element.find_element(By.CLASS_NAME, "room-title").get_attribute("innerText")
        if name in seen:
            continue
        link = element.find_element(By.TAG_NAME, "a").get_attribute("href")
        people = element.find_element(By.CLASS_NAME, "room-count-people").get_attribute("innerText")
        people = int(people.split()[0])
        results.append(Room(name=name, link=link, people=people))
        seen.add(name)
    return results


def get_elements_by_class(driver: WebDriver, class_name: str, max_number: Optional[int] = None) -> list[WebElement]:
    # wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

    elements = driver.find_elements(By.CLASS_NAME, class_name)
    if max_number:
        return elements[:max_number]
    return elements


def click_element_by_class(driver: WebDriver, class_name: str) -> None:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    driver.find_element(By.CLASS_NAME, class_name).click()


def click_element_by_attribute(driver: WebDriver, css_selector: str) -> None:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    driver.find_element(By.CSS_SELECTOR, css_selector).click()


def type_text_to_field(driver: WebDriver, id: str, text: str) -> None:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, id)))
    driver.find_element(By.ID, id).send_keys(text)
