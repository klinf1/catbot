import asyncio
import os
# from datetime import datetime as dt

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from sqlmodel import select, and_
from telegram import Bot

from db import Ages, Characters, DbBrowser, PreyPile, Settings, engine, SQLModel
from db.seasons import SeasonsConfig
from logs.logs import schedule_logger as logger

load_dotenv()
db = DbBrowser()
active_chars = select(Characters).where(and_(Characters.is_dead == False, Characters.is_frozen == False))  #noqa: E712
scheduler = BackgroundScheduler()


def create_schedules() -> None:
    logger.debug("schedule creation start")
    store = SQLAlchemyJobStore(engine=engine, metadata=SQLModel.metadata)    
    scheduler.add_jobstore(store)
    scheduler.start()
    if not store.get_all_jobs():
        logger.debug("No jobs found, creating...")
        scheduler.add_job(advance_seasons, 'cron', name="advance_seasons", minute=1)  # day=1
        scheduler.add_job(cut_pile, 'cron', name="cut_pile", minute=1)
        scheduler.add_job(check_nutrition, 'cron', name="check_nutrition", minute=1)
        scheduler.add_job(age_cats, 'cron', name="age_cats", minute=1)
        scheduler.add_job(reset_hunt_attempts, 'cron', name="reset_hunt_attempts", second=2)  # day_of_week=0
    logger.debug("Schedule creation end")


def check_nutrition():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_check_nutrition())


def age_cats():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_age_cats())


def advance_seasons():
    logger.info("Season advance start")
    SeasonsConfig().set_next_season()
    logger.info("Season advance end")


def cut_pile():
    db = DbBrowser()
    logger.info("Pile cutting start")
    piles: list[PreyPile] = db.select_many(select(PreyPile))
    clan_list = {i.clan for i in piles}
    for clan in clan_list:
        logger.info(f"cutting for clan no {clan}")
        prey_list = sorted([i for i in piles if i.clan == clan], key=lambda v: v.date_added)
        old = prey_list[:len(prey_list)//2]
        for i in old:
            db.delete(i)
    logger.info("Pile cutting end")


async def _check_nutrition():
    logger.info("Nutrition check start")
    db = DbBrowser()
    bot = Bot(token=os.getenv("TOKEN"))
    chars: list[Characters] = db.select_many(active_chars)
    max_hunger: Settings = db.select_one(select(Settings).where(Settings.name == "max_hunger"))
    for char in chars:
        age_q = select(Ages).where(Ages.max_age > char.age).order_by(Ages.max_age)
        age: Ages = db.safe_select_one(age_q)
        if age.food_req > char.nutrition:
            char.hunger += 1
            if char.hunger > int(max_hunger.value):
                char.is_dead = True
                db.add(char)
                logger.info(f"Character {char.name} died of hunger UwU")
                await bot.send_message(
                    char.player_chat_id,
                    f"Ваш персонаж {char.name} умер от голода!"
                )
                continue
            db.add(char)
            logger.debug(f"Hunger added for {char.name} new {char.hunger}")            
        if char.nutrition >= age.food_req and char.hunger != 0:
            logger.debug(f"Hunger reset for {char.name}")
            char.hunger = 0
            db.add(char)
    logger.info("Nutrition check end")


async def _age_cats():
    logger.info("Age start")
    bot = Bot(token=os.getenv("TOKEN"))
    db = DbBrowser()
    admin_chat = os.getenv("ADMIN_CHAT")
    ages = select(Ages)
    chars: list[Characters] = db.select_many(active_chars)
    ages: list[Ages] = db.select_many(ages)
    breakpoints = [age.max_age for age in ages]
    max_age: Settings = db.select_one(select(Settings).where(Settings.name == "max_age"))
    for char in chars:
        char.age += 2
        if char.age in breakpoints:
            if char.age >= int(max_age.value):
                logger.info(f"Char {char.name} died of old age.")
                char.is_dead = True
                await bot.send_message(char.player_chat_id, f"Ваш персонаж {char.name} умер от старости.")
            else:
                logger.info(f"Char {char.name} grown to {char.age} moons.")
                await bot.send_message(admin_chat, f"Персонаж {char.name} вырос до {char.age} лун! Нужно сменить ему характеристики!")
        db.add(char)
    logger.info("Age end")


def reset_hunt_attempts():
    logger.info("Hunt attemps start")
    db = DbBrowser()
    chars: list[Characters] = db.select_many(active_chars)
    for char in chars:
        char.curr_hunts = 0
        db.add(char)
    logger.info("Hunt attemps end")
