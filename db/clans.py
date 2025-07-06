from typing import Any

from sqlmodel import Session, select

from db import Clans, DbBrowser


class DbClanConfig(DbBrowser):
    session: Session

    def __init__(self) -> None:
        super().__init__()

    def get_all_clans(self):
        return self.session.exec(select(Clans)).all()

    def get_clan_by_name(self, name: str) -> Clans:
        query = select(Clans).where(Clans.name == name)
        with self.session as s:
            return s.exec(query).one()

    def get_clan_by_no(self, no: int) -> Clans:
        query = select(Clans).where(Clans.no == no)
        with self.session as s:
            return s.exec(query).one()

    def add_new_clan(self, params: dict[str, Any]):
        new_clan = Clans(**params)
        self.add(new_clan)

    def rename_clan(self, name: str, new_name: str):
        clan = self.get_clan_by_name(name)
        clan.name = new_name
        self.add(clan)

    def edit_prey_pile(self, clan_no: int, value: int):
        clan = self.get_clan_by_no(clan_no)
        clan.prey_pile_percent += value
        self.add(clan)

    def appoint_leader(self, clan_no, new_leader: int):
        clan = self.get_clan_by_no(clan_no)
        clan.leader = new_leader
        self.add(clan)

    def delete_clan_by_no(self, no: int):
        clan = self.get_clan_by_no(no)
        self.delete(clan)
