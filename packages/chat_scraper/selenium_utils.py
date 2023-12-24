from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_elements_by_class(driver: WebDriver, class_name: str, url: str) -> list[WebElement]:
    driver.get(url)
    # wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

    elements = driver.find_elements(By.CLASS_NAME, class_name)
    return elements
