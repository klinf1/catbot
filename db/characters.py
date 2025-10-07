from typing import Any

from sqlmodel import Session, and_, select

from db import Characters, DbBrowser
from db.clans import DbClanConfig
from exceptions import NotRealClanError


class DbCharacterUser(DbBrowser):
    session: Session

    def __init__(self, chat_id: int) -> None:
        super().__init__()
        self.chat_id = chat_id

    def get_all_own_chars(self):
        query = select(Characters).where(Characters.player_chat_id == self.chat_id)
        with self.session as s:
            return s.exec(query).all()

    def get_one_own_char(self, name: str):
        query = select(Characters).where(
            and_(Characters.player_chat_id == self.chat_id, Characters.name == name)
        )
        with self.session as s:
            return s.exec(query).first()


class DbCharacterConfig(DbBrowser):
    session: Session

    def __init__(self) -> None:
        super().__init__()

    def get_char_by_name(self, name: str):
        query = select(Characters).where(Characters.name == name)
        with self.session as s:
            return s.exec(query).first()

    def get_char_by_no(self, no: int):
        query = select(Characters).where(Characters.no == no)
        with self.session as s:
            return s.exec(query).first()

    def get_chars_for_player(self, chat_id: int):
        query = select(Characters).where(Characters.player_chat_id == chat_id)
        with self.session as s:
            cats = s.exec(query).all()
        return cats

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

    def edit_character(self, name, params: dict[str, Any]):
        char = self.get_char_by_name(name)
        for column, value in params.items():
            char = self._edit_single_stat(char, column, value)
        self.add(char)

    def delete_character_by_no(self, no: int):
        char = self.get_char_by_no(no)
        self.delete(char)

    def edit_freeze_char_by_no(self, no: int, flag: bool = True):
        char = self.get_char_by_no(no)
        char.is_frozen = flag
        self.add(char)
    
    def edit_freeze_char_by_name(self, name: str, flag: bool = True):
        char = self.get_char_by_name(name)
        char.is_frozen = flag
        self.add(char)

    def edit_death_char_by_no(self, no: int, flag: bool = True):
        char = self.get_char_by_no(no)
        char.is_dead = flag
        self.add(char)

    def check_if_char_belongs_to_clan(self, char_no: int, clan: int) -> bool:
        query = select(Characters).where(Characters.no == char_no)
        with self.session as s:
            char = s.exec(query).one()
        return True if char.clan_no == clan else False

    def get_all_chars(self):
        query = select(Characters)
        with self.session as s:
            chars = s.exec(query).all()
        return chars

    @staticmethod
    def _edit_single_stat(char: Characters, stat: str, value: Any):
        print(stat, value)
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
