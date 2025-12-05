import os
import sys

from dotenv import load_dotenv


from bot.main import bot_main
from db import DbBrowser, create_tables
from debug_tables import create_test_data
from logs.logs import main_logger as logger
from schedule import create_schedules

load_dotenv()


def main():
    token = os.getenv("TOKEN")
    admin_ids = os.getenv("ADMINS", "").split(",")
    admin_names = os.getenv("ADMIN_NAMES", "").split(",")
    try:
        create_tables()
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        logger.error(os.getenv("DB_PATH"))
        sys.exit(1)
    print("Tables created!")
    create_schedules()
    print("Jobs scheduled!")
    DbBrowser().add_admins(admin_ids, admin_names)
    if os.getenv("TEST_MODE"):
        create_test_data()
        print("Test data added!")
    logger.info("Starting bot process...")
    bot_main(token)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass