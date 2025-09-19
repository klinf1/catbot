from typing import Any

from sqlmodel import Session, and_, select

from db import Clans, DbBrowser, Prey, PreyTerritory
from db.clans import DbClanConfig


class DbPreyConfig(DbBrowser):
    session: Session

    def __init__(self) -> None:
        super().__init__()

    def refresh(self):
        self.session.refresh(Prey)
        self.session.refresh(PreyTerritory)

    def get_all_prey(self):
        with self.session as s:
            return s.exec(select(Prey)).all()

    def get_prey_by_name(self, name: str) -> Prey:
        query = select(Prey).where(Prey.name == name)
        with self.session as s:
            return s.exec(query).one()

    def get_prey_by_no(self, no: int) -> Prey:
        query = select(Prey).where(Prey.no == no)
        with self.session as s:
            return s.exec(query).one()

    def get_prey_for_territory_no(self, terr_no: int | None):
        query = select(Prey).where(Prey.territory == terr_no)
        with self.session as s:
            return s.exec(query).all()

    def add_new_prey(self, params: dict[str, Any]):
        terr: str = params.get("territory")
        territories = []
        if terr:
            terr_list = terr.split(";")
            for i in terr_list:
                try:
                    int(i.strip())
                    territories.append(i)
                except ValueError:
                    j = DbClanConfig().get_clan_by_name(i.strip())
                    territories.append(j.no)
        del params["territory"]
        new_prey = Prey(**params)
        self.add(new_prey)
        self.session.refresh(Prey)
        added_prey: Prey = self.select_one(
            select(Prey).where(Prey.name == new_prey.name)
        )
        for i in territories:
            new_terr_link = PreyTerritory(prey=added_prey.no, territory=terr)
        self.add(new_terr_link)

    def edit_prey_by_name(self, name: str, params: dict[str, Any]):
        prey = self.get_prey_by_name(name)
        for column, value in params.items():
            prey = self._edit_single_stat(prey, column, value)
        self.add(prey)

    def delete_prey_by_no(self, no: int):
        prey = self.get_prey_by_no(no)
        self.delete(prey)

    @staticmethod
    def _edit_single_stat(prey: Prey, column: str, value: Any):
        setattr(prey, column, value)
        return prey

    def new_prey_territory(self, prey: Prey, terr: Clans):
        new_terr = PreyTerritory(prey=prey.no, territory=terr.no)
        self.add(new_terr)

    def remove_prey_terr(self, prey: Prey, terr: Clans):
        query = select(PreyTerritory).where(
            and_(PreyTerritory.prey == prey.no, PreyTerritory.territory == terr.no)
        )
        old_terr = self.safe_select_one(query)
        if old_terr:
            self.delete(old_terr)

    def reset_territories(self, prey: Prey, terr: str):
        query = select(PreyTerritory).where(PreyTerritory.prey == prey.no)
        old_terr = self.select_many(query)
        for i in old_terr:
            self.delete(i)
        new_terr = terr.split(";")
        for i in new_terr:
            try:
                int(i)
                territory = DbClanConfig().get_clan_by_no(i)
            except ValueError:
                territory = DbClanConfig().get_clan_by_name(i)
            db_terr = PreyTerritory(prey=prey.no, territory=territory.no)
            self.add(db_terr)
