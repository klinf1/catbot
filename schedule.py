import asyncio
import os

from sqlmodel import select, and_
from telegram import Bot

from db import Ages, Characters, DbBrowser, PreyPile
from db.seasons import SeasonsConfig
from logs.logs import schedule_logger as logger

db = DbBrowser()
bot = Bot(token=os.getenv("TOKEN"))
admin_chat = os.getenv("ADMIN_CHAT")
active_chars = select(Characters).where(and_(Characters.is_dead == False, Characters.is_frozen == False))  #noqa: E712


def monthly_jobs():
    advance_seasons()
    cut_pile()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(async_jobs())


def weekly_jobs():
    reset_hunt_attempts()


async def async_jobs():
    await check_nutrition()
    await age_cats()


def advance_seasons():
    logger.info("Season advance start")
    SeasonsConfig().set_next_season()
    logger.info("Season advance end")


async def check_nutrition():
    logger.info("Nutrition check start")
    chars: list[Characters] = db.select_many(active_chars)
    for char in chars:
        age_q = select(Ages).where(Ages.max_age > char.age).order_by(Ages.max_age)
        age: Ages = db.safe_select_one(age_q)
        if age.food_req > char.nutrition:
            char.hunger += 1
            db.add(char)
            logger.debug(f"Hunger added for {char.name} new {char.hunger}")
            await bot.send_message(
                    char.player_chat_id,
                    f"Ваш персонаж {char.name} недостаточно поел в прошлом сезоне и получил одну степень голода!"
                    f" Текущий голод равен {char.hunger}",
                )
            
        if char.nutrition >= age.food_req and char.hunger != 0:
            logger.debug(f"Hunger reset for {char.name}")
            char.hunger = 0
            db.add(char)
    logger.info("Nutrition check end")


def cut_pile():
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


async def age_cats():
    logger.info("Age start")
    ages = select(Ages)
    chars: list[Characters] = db.select_many(active_chars)
    ages: list[Ages] = db.select_many(ages)
    breakpoints = [age.max_age for age in ages]
    for char in chars:
        char.age += 2
        if char.age in breakpoints:
            if char.age >= 150:
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
    chars: list[Characters] = db.select_many(active_chars)
    for char in chars:
        char.curr_hunts = 0
        db.add(char)
    logger.info("Hunt attemps end")
