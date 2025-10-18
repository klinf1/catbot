from datetime import datetime as dt
import os

from dotenv import load_dotenv
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from bot.main import bot_main
from db import DbBrowser, create_tables, engine, SQLModel
from debug_tables import create_test_data
from logs.logs import main_logger as logger
from schedule import monthly_jobs, weekly_jobs

load_dotenv()


def create_schedules() -> None:
    logger.debug("Schedule creation start")
    store = SQLAlchemyJobStore(engine=engine, metadata=SQLModel.metadata)
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(store)
    scheduler.start()
    if not store.get_all_jobs():
        logger.debug("No jobs found, creating...")
        scheduler.add_job(monthly_jobs, 'cron', second=1)  # day=dt.now().day
        scheduler.add_job(weekly_jobs, 'cron', second=2)  # day_of_week=dt.now().weekday()
    else:
        logger.debug("Jobs already exist, starting scheduler...")
    logger.debug("Schedule creation end")

def main():
    token = os.getenv("TOKEN")
    admin_ids = os.getenv("ADMINS", "").split(",")
    admin_names = os.getenv("ADMIN_NAMES", "").split(",")
    create_tables()
    print("Tables created!")
    create_schedules()
    print("Jobs scheduled!")
    DbBrowser().add_admins(admin_ids, admin_names)
    if os.getenv("TEST_MODE"):
        create_test_data()
        print("Test data added!")
    print("Starting bot...")
    bot_main(token)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass