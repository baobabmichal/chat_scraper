from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

from packages.common.data_model import MainMessage


class MessageUpdater:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.messages: list[MainMessage] = []

    def update(self):
        if not self.messages:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m-messagesTextArea")))
        text_area = self.driver.find_element(By.CLASS_NAME, "m-messagesTextArea")
        message_elements = text_area.find_elements(By.CLASS_NAME, "m-msg-item-user-message")
        new_message_elements = message_elements[len(self.messages) :]
        print(f"New messages: {len(new_message_elements)}")
        for element in tqdm(new_message_elements):
            user_name, message = element.get_attribute("innerText").split(":", maxsplit=1)
            self.messages.append(MainMessage(user_name=user_name, message=message))
