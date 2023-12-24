from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


def get_pretty_html_from_driver(driver: WebDriver) -> str:
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.prettify()


def get_pretty_html_from_selenium_element(element: WebElement) -> str:
    html_content = element.get_attribute("innerHTML")
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.prettify()
