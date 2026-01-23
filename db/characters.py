from typing import Any, Literal

from sqlmodel import and_, select

from db import Characters, CharacterHistory, DbBrowser
from db.clans import DbClanConfig
from exceptions import CharNotFound, NotRealClanError


class DbCharacterUser(DbBrowser):
    def __init__(self, chat_id: int) -> None:
        super().__init__()
        self.chat_id = chat_id

    def get_all_own_chars(self):
        query = select(Characters).where(Characters.player_chat_id == self.chat_id)
        return self.select_many(query)

    def get_one_own_char(self, name: str):
        query = select(Characters).where(and_(Characters.player_chat_id == self.chat_id, Characters.name == name))
        return self.safe_select_one(query)


class DbCharacterConfig(DbBrowser):
    def __init__(self, admin: str | None = "") -> None:
        super().__init__()
        self.admin = admin

    def get_char_by_name(self, name: str) -> Characters | None:
        query = select(Characters).where(Characters.name == name)
        return self.safe_select_one(query)

    def get_char_by_no(self, no: int):
        query = select(Characters).where(Characters.no == no)
        return self.safe_select_one(query)

    def get_chars_for_player(self, chat_id: int):
        query = select(Characters).where(Characters.player_chat_id == chat_id)
        return self.select_many(query)

    def add_character(self, params: dict):
        try:
            int(params.get("clan_no", "-100"))
        except ValueError:
            clan = DbClanConfig().get_real_clan(params["clan_no"])
            if clan:
                params["clan_no"] = clan.no
            else:
                raise NotRealClanError
        char = Characters(**params)
        self.add(char)

    def edit_character(self, name: str, params: dict[str, Any], reason: str):
        char = self.get_char_by_name(name)
        if not char:
            raise CharNotFound
        for column, value in params.items():
            self.ins_char_hist(char.no, self.admin, column, getattr(char, column), str(value), reason)
            char = self._edit_single_stat(char, column, value)
        self.add(char)

    def delete_character_by_no(self, no: int):
        char = self.get_char_by_no(no)
        self.delete(char)

    def edit_freeze_char_by_no(self, no: int, reason: str, flag: bool = True):
        char = self.get_char_by_no(no)
        self.ins_char_hist(char.no, self.admin, "is_frozen", str(char.is_frozen), str(flag), reason)
        char.is_frozen = flag
        self.add(char)

    def edit_freeze_char_by_name(self, name: str, reason: str, flag: bool = True):
        char = self.get_char_by_name(name)
        self.ins_char_hist(char.no, self.admin, "is_frozen", str(char.is_frozen), str(flag), reason)
        char.is_frozen = flag
        self.add(char)

    def edit_death_char_by_no(self, no: int, reason: str, flag: bool = True):
        char = self.get_char_by_no(no)
        self.ins_char_hist(char.no, self.admin, "is_dead", str(char.is_dead), str(flag), reason)
        char.is_dead = flag
        self.add(char)

    def edit_death_char_by_name(self, name: str, reason: str, flag: bool = True):
        char = self.get_char_by_name(name)
        self.ins_char_hist(char.no, self.admin, "is_dead", str(char.is_dead), str(flag), reason)
        char.is_dead = flag
        self.add(char)

    def check_if_char_belongs_to_clan(self, char_no: int, clan: int) -> bool:
        query = select(Characters).where(Characters.no == char_no)
        char = self.select_one(query)
        return True if char.clan_no == clan else False

    def get_all_chars(self):
        query = select(Characters)
        return self.select_many(query)

    @staticmethod
    def _edit_single_stat(char: Characters, stat: str, value: Any):
        if stat == "clan_no":
            try:
                int(value)
            except ValueError:
                clan = DbClanConfig().get_real_clan(value)
                if clan:
                    value = clan.no
                else:
                    raise NotRealClanError
        setattr(char, stat, value)
        return char

    def get_char_history(self, name: str) -> list[CharacterHistory]:
        char: Characters = self.get_char_by_name(name)
        if not char:
            raise CharNotFound
        query = select(CharacterHistory).where(CharacterHistory.char_no == char.no)
        return self.select_many(query)

    def get_admin_history(self, admin: str) -> list[CharacterHistory]:
        query = select(CharacterHistory).where(CharacterHistory.user == admin)
        return self.select_many(query)

    def set_curr_hunts(self, name: str, new: int, reason: str) -> Literal[True]:
        char = self.get_char_by_name(name)
        if not char:
            raise CharNotFound
        self.edit_character(char.name, {"curr_hunts": new}, reason)
        return True
