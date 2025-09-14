import os

from dotenv import load_dotenv

from bot.main import bot_main
from db import AtStart, create_tables

load_dotenv()


def main():
    token = os.getenv("TOKEN")
    admin_ids = os.getenv("ADMINS", '').split(",")
    admin_names = os.getenv("ADMIN_NAMES", '').split(",")
    create_tables()
    AtStart().add_admins(admin_ids, admin_names)
    bot_main(token)


if __name__ == "__main__":
    main()
