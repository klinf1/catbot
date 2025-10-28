SETTINGS = [
    {'name': 'hunt_attempts', 'value': '5'},
    {'name': 'max_hunger', 'value': '3'},
    {'name': 'hunger_pen_1', 'value': '1'},
    {'name': 'hunger_pen_2', 'value': '3'},
    {'name': 'hunger_pen_3', 'value': '5'},
    {'name': 'max_age', 'value': '150'}
]

SEASONS = [
    {"name": "Весна", "hunt_mod": -25, "herb_mod": 0, "is_active": False, "next": "Лето"},
    {"name": "Лето", "hunt_mod": 0, "herb_mod": 0, "is_active": True, "next": "Осень"},
    {"name": "Осень", "hunt_mod": -25, "herb_mod": 0, "is_active": False, "next": "Зима"},
    {"name": "Зима", "hunt_mod": -50, "herb_mod": 0, "is_active": False, "next": "Весна"},
]

AGES = [
    {"name": "Котенок", "max_age": 6, "food_req": 1, "next": "Подросток"},
    {"name": "Подросток", "max_age": 12, "food_req": 3, "next": "Взрослый"},
    {"name": "Взрослый", "max_age": 150, "food_req": 5},
]

CLANS = [
    {"name": "Клан добрых", "is_true_clan": True},
    {"name": "Территория злых", "is_true_clan": False}
]
