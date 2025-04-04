from SQLuser import ask_user
from SQLcreate import database
from SQLcoder import sql_driver
from AddUser import add_new_user
from DebugLog import log_error


def main_menu():
    while True:
        print("\n=== Main Menu ===")
        print("1. Run SQL AI (SQLcoder)")
        print("2. Create/edit database")
        print("3. Add new user (admin only)")
        print("0. Logout / Exit")

        choice = input("Choose action: ")

        if choice == "1":
            sql_driver()
        elif choice == "2":
            database()
        elif choice == "3":
            add_new_user()
        elif choice == "0":
            print("Logging out. Goodbye!")
            break
        else:
            print("Invalid choice.")

def start():
    try:
        if ask_user():
            main_menu()
        else:
            print('Login failure')
            log_error('Login failure')
    except Exception as e:
        print(f'Unexpected error: {e}')
        log_error(f'Unexpected error in start(): {e}')


if __name__ == '__main__':
    start()
