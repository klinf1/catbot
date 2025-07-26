from typing import overload

from db import Characters, DbBrowser, Prey
from db.characters import DbCharacterConfig
from db.prey import DbPreyConfig


class Eater(DbBrowser):
    def __init__(self) -> None:
        super().__init__()
        self.prey_db = DbPreyConfig()
        self.char_db = DbCharacterConfig()

    @overload
    def eat(self, char: int, prey: int) -> str: ...

    @overload
    def eat(self, char: Characters, prey: Prey) -> str: ...

    @overload
    def eat(self, char: int, prey: Prey) -> str: ...

    @overload
    def eat(self, char: Characters, prey: int) -> str: ...

    def eat(self, char: int | Characters, prey: int | Prey) -> str:
        if isinstance(char, int):
            char = self.char_db.get_char_by_no(char)
        if isinstance(prey, int):
            prey = self.prey_db.get_prey_by_no(prey)
        char.nutrition += prey.amount
        self.add(char)
        return f"{char.name} съел {prey.name}!"
