import traceback
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), "../logs/ErrorLog.log")

def log_error(error_message):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"Error: {error_message}\n")
        log.write(traceback.format_exc())
        log.write("\n" + "=" * 40 + "\n")