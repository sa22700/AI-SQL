from core.SQLuser import ask_user
from core.SQLcreate import database
from core.SQLcoder import sql_driver
from core.AddUser import add_new_user
from core.DebugLog import log_error
from core.DelUser import delete_user
from core.DelTable import drop_table
from core.DelParts import delete_part
from core.UpdParts import update_part
from ui.Utils import clean_rows


def main_menu() -> None:
    while True:
        print("\n--- Main Menu ---")
        print("1. Run SQL AI (SQLcoder)")
        print("2. Create database (admin only)")
        print("3. Add new user (admin only)")
        print("4. Delete user (admin only)")
        print("5. Delete table (admin only)")
        print("6. Delete parts (admin only)")
        print("7. Update parts (admin only)")
        print("0. Logout / Exit")
        while True:
            try:
                choice = int(input("Choose action: "))
                break
            except ValueError:
                print("Invalid choice. Please enter a number.")
        if choice == 1:
            result = sql_driver()
            print(clean_rows(result.get("sql", "")))
            print(clean_rows(result.get("rows", "")))
        elif choice == 2:
            database()
        elif choice == 3:
            add_new_user()
        elif choice == 4:
            delete_user()
        elif choice == 5:
            drop_table()
        elif choice == 6:
            delete_part()
        elif choice == 7:
            update_part()
        elif choice == 0:
            print("Logging out. Goodbye!")
            break
        else:
            print("Invalid choice.")

def start() -> None:
    try:
        auth = ask_user()
        if isinstance(auth, dict):
            if auth.get("ok"):
                main_menu()
            else:
                msg = auth.get("error", "Login failure")
                print(msg)
                log_error(msg)
            return
        if auth:
            main_menu()
        else:
            print("Login failure")
            log_error("Login failure")

    except Exception as e:
        print(f"Unexpected error: {e}")
        log_error(f"Unexpected error in start(): {e}")

if __name__ == '__main__':
    start()
