from sqlmodel import Session, and_, select

from db import PreyPile, Prey, DbBrowser, Clans
from db.clans import DbClanConfig
from db.prey import DbPreyConfig


class PreyPileConfig(DbBrowser):
    session: Session

    def __init__(self) -> None:
        super().__init__()
        self.clan_db = DbClanConfig()
        self.prey_db = DbPreyConfig()
    
    def _get_prey(self, prey: int | str | Prey) -> Prey:
        if isinstance(prey, int):
            prey = self.prey_db.get_prey_by_no(prey)
        elif isinstance(prey, str):
            prey = self.prey_db.get_prey_by_name(prey)
        return prey
    
    def _get_clan(self, clan: int | str| Clans) -> Clans:
        if isinstance(clan, int):
            clan = self.clan_db.get_clan_by_no(clan)
        elif isinstance(clan, str):
            clan = self.clan_db.get_clan_by_name(clan)
        return clan
    
    def add_to_pile(self, clan: int | str| Clans, prey: int | str | Prey):
        clan = self._get_clan(clan)
        prey = self._get_prey(prey)
        new_pile = PreyPile(clan.no, prey.no)
        self.add(new_pile)
        return f"Дичь {prey.name} добавлена в кучу клана {clan.name}"
    
    def get_from_pile(self, clan: int | str| Clans, prey: int | str | Prey):
        clan = self._get_clan(clan)
        prey = self._get_prey(prey)
        query = select(PreyPile).where(and_(PreyPile.clan == clan.no, PreyPile.prey == prey.no))
        item = self.safe_select_one(query)
        if item:
            self.delete(item)

