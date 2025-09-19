from typing import Any, overload

from sqlmodel import Session, and_, select

from db import Clans, DbBrowser


class DbClanConfig(DbBrowser):
    session: Session

    def __init__(self) -> None:
        super().__init__()

    def get_all_clans(self):
        return self.session.exec(select(Clans).where(Clans.is_true_clan is True)).all()

    def get_all_territories(self):
        return self.session.exec(select(Clans).where(Clans.is_true_clan is False)).all()

    def get_clan_by_name(self, name: str) -> Clans:
        query = select(Clans).where(Clans.name == name)
        with self.session as s:
            return s.exec(query).first()

    def get_clan_by_no(self, no: int) -> Clans:
        query = select(Clans).where(Clans.no == no)
        with self.session as s:
            return s.exec(query).first()

    def add_new_clan(self, params: dict[str, Any]):
        if params.get("is_true_clan"):
            params["is_true_clan"] = True
        else:
            params["is_true_clan"] = False
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

    @overload
    def appoint_leader(self, clan_id: int, new_leader: int): ...

    @overload
    def appoint_leader(self, clan_id: str, new_leader: int): ...

    def appoint_leader(self, clan_id: int | str, new_leader: int):
        if isinstance(clan_id, str):
            clan = self.get_clan_by_name(clan_id)
        else:
            clan = self.get_clan_by_no(clan_id)
        clan.leader = new_leader
        self.add(clan)

    def remove_leader(self, clan_id: str | int):
        if isinstance(clan_id, str):
            clan = self.get_clan_by_name(clan_id)
        else:
            clan = self.get_clan_by_no(clan_id)
        clan.leader = None
        self.add(clan)

    def delete_clan_by_no(self, no: int):
        clan = self.get_clan_by_no(no)
        self.delete(clan)

    def get_real_clan(self, id: str | int) -> Clans | None:
        if isinstance(id, str):
            query = select(Clans).where(
                and_(Clans.name == id, Clans.is_true_clan is True)
            )
        else:
            query = select(Clans).where(
                and_(Clans.no == id, Clans.is_true_clan is True)
            )
        return self.safe_select_one(query)
