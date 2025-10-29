from sqlmodel import select

from db import Prey, Characters, DbBrowser, PreyPile

db = DbBrowser()


def create_test_data():
    char_data = [{"name": "Тест_котенок", "player_chat_id": 397012508, "age": 2, "hunting": 1, "clan_no": 1},
                 {"name": "Тест_подросток", "player_chat_id": 397012508, "age": 8, "hunting": 5},
                 {"name": "Тест_взрослый", "player_chat_id": 397012508, "age": 14, "hunting": 10}]
    prey_data = [
        {"name": "Тест_легкая", "stat": "agility", "amount": 1, "rarity": 100, "sum_required": 1},
        {"name": "Тест_средняя", "stat": "agility", "amount": 2, "rarity": 50, "sum_required": 5},
        {"name": "Тест_сложная", "stat": "agility", "amount": 5, "rarity": 20, "sum_required": 10},
    ]
    prey_pile_data = [
        {"clan": 1, "prey": 1},
        {"clan": 1, "prey": 1},
        {"clan": 1, "prey": 1},
        {"clan": 1, "prey": 1},
        {"clan": 1, "prey": 1},
        {"clan": 1, "prey": 1},
        {"clan": 1, "prey": 1},
    ]
    if not db.safe_select_one(select(Characters)):
        for i in char_data:
            db.add(Characters(**i))
    if not db.safe_select_one(select(Prey)):
        for i in prey_data:
            db.add(Prey(**i))
    if not db.safe_select_one(select(PreyPile)):
        for i in prey_pile_data:
            db.add(PreyPile(**i))