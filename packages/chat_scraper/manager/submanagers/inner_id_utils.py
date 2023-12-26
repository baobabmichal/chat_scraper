from selenium.webdriver.remote.webelement import WebElement


def extract_id(element: WebElement) -> int:
    return element.get_attribute("id").split("-")[-1]
