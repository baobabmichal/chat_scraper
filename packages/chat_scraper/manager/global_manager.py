from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from packages.chat_scraper.manager.submanagers.room_manager import RoomManager
from packages.common.data_model import PageStatus


class GlobalManager:
    def __init__(self, driver: WebDriver, room_url: Optional[str] = None, room_name: Optional[str] = None) -> None:
        self.driver = driver
        self.room_manager: Optional[RoomManager] = None

        if room_url and room_name:
            self.driver.get(room_url)
            self.page_status = PageStatus.login_page
            self.room_name = room_name
        else:
            self.page_status: PageStatus = PageStatus.main_page
            self.room_name: Optional[str] = None
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "room-item")))

    def get_into_room(self, room_name: str) -> None:
        assert self.page_status == PageStatus.main_page
        room_elements = self.driver.find_elements(By.CLASS_NAME, "room-item")
        print(f"Getting into room {room_name}")
        for element in room_elements:
            name = element.find_element(By.CLASS_NAME, "room-title").get_attribute("innerText")
            if name.lower() == room_name.lower():
                link = element.find_element(By.TAG_NAME, "a").get_attribute("href")
                self.driver.get(link)
                self.page_status = PageStatus.login_page
                self.room_name = room_name
                return

    def log_into(self, user_login: str, user_password: str) -> None:
        print(f"Logging into as {user_login}")
        assert self.page_status == PageStatus.login_page
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "rodo-popup-agree")))
        self.driver.find_element(By.CLASS_NAME, "rodo-popup-agree").click()
        self.driver.find_element(By.CSS_SELECTOR, '[for="login-user"]').click()
        self.driver.find_element(By.ID, "nick-login").send_keys(user_login)
        self.driver.find_element(By.ID, "password-login").send_keys(user_password)
        self.driver.find_element(By.ID, "enter-login").click()
        self.page_status = PageStatus.room_page
        self.room_manager = RoomManager(self.driver, room_name=self.room_name)

    def save_page_source(self, file_path: Path = Path("source.html")) -> None:
        html_content = self.driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        pretty_html = soup.prettify()
        with open(file_path, "wt") as f:
            f.write(pretty_html)

    def check_page_status(self) -> None:
        try:
            if self.page_status == PageStatus.main_page:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "rooms-categories")))
            elif self.page_status == PageStatus.login_page:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "nick-login")))
            elif self.page_status == PageStatus.room_page:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "m-messagesTextArea"))
                )
        except TimeoutException as e:
            raise (e)
