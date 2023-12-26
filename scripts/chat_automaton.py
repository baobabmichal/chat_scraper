import os

from dotenv import load_dotenv
from selenium import webdriver

from packages.chat_scraper.manager.global_manager import GlobalManager

load_dotenv()
ROOM = os.environ["ROOM"]
ROOM_URL = os.environ["ROOM_URL"]
USER_LOGIN = os.environ["USER_LOGIN"]
USER_PASSWORD = os.environ["USER_PASSWORD"]


def main():
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    # driver.minimize_window()

    manager = GlobalManager(driver, room_url=ROOM_URL, room_name=ROOM)
    manager.log_into(USER_LOGIN, USER_PASSWORD)

    while True:
        option = input("Choose option:")
        try:
            if option == "q":
                manager.driver.close()
                quit()
            elif option == "save":
                manager.save_page_source()
            elif option == "new":
                manager.room_manager.open_chat_random_registered_user()
            elif option == "print":
                manager.room_manager.print_current_tab_info()
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
            else:
                manager.room_manager.send_message(option)
        except Exception as e:
            manager.save_page_source()
            manager.driver.close()
            raise (e)


if __name__ == "__main__":
    main()
