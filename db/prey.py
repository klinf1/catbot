from typing import Any

from sqlmodel import Session, select

from db import DbBrowser, Prey


class DbPreyConfig(DbBrowser):
    session: Session

    def __init__(self) -> None:
        super().__init__()

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
        new_prey = Prey(**params)
        self.add(new_prey)

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
