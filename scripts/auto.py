import os
import re

from dotenv import load_dotenv
from selenium import webdriver

from packages.chat_scraper.manager.global_manager import GlobalManager

load_dotenv()
ROOM = os.environ["ROOM"]
ROOM_URL = os.environ["ROOM_URL"]
USER_LOGIN = os.environ["USER_LOGIN"]
USER_PASSWORD = os.environ["USER_PASSWORD"]

REGEX = os.environ["REGEX"]
PATTERN = re.compile(REGEX)

MESSAGE = os.environ["MESSAGE"]
DATA_PATH = os.environ["DATA_PATH"]


def main():
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    # driver.minimize_window()

    manager = GlobalManager(driver, room_url=ROOM_URL, room_name=ROOM, data_path=DATA_PATH)
    manager.log_into(USER_LOGIN, USER_PASSWORD)

    while True:
        option = input("Choose option:")
        try:
            manager.room_manager._update_statuses()
            manager.room_manager._purge_all()
            manager.room_manager.print_unseen()
            if option == "q":
                manager.driver.close()
                quit()
            elif option == "save":
                manager.room_manager.save_data()
            elif option == "load":
                manager.room_manager.load_data()
            elif option == "debug":
                manager.room_manager.print_unseen()
            elif option == "html":
                manager.save_page_source()
            elif option == "new" or option == "":
                manager.room_manager.open_chat_random_registered_user(PATTERN)
                if manager.room_manager.tab_active != manager.room_manager.room_id:
                    manager.room_manager.send_message(MESSAGE)
            elif option == "print":
                manager.room_manager.print_tab_info_current()
            elif option == "close":
                manager.room_manager.close_current_tab()
            elif option == "tabs":
                print(manager.room_manager._all_tabs())
            elif option.isnumeric() and int(option) in list(range(manager.room_manager._count_tabs())):
                tab_chosen = manager.room_manager._all_tabs()[int(option)]
                manager.room_manager._choose_tab(tab_chosen)
                continue
            elif option == "room":
                manager.room_manager._choose_room()
            elif manager.room_manager.tab_active == manager.room_manager.room_id:
                manager.room_manager.open_chat_random_registered_user(re.compile(option))
                manager.room_manager.send_message(MESSAGE)
            else:
                manager.room_manager.send_message(option)
        except Exception as e:
            manager.save_page_source()
            manager.driver.close()
            raise (e)


if __name__ == "__main__":
    main()
