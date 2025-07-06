from random import randint


def roll(die_size: int = 10) -> int:
    return randint(1, die_size)
