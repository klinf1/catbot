from random import choice, randint

from sqlmodel import Session, and_, or_, select

from db import CharacterInventory, Characters, Clans, DbBrowser, Herbs
from logs.logs import main_logger as logger
from roll import roll


class HerbUser(DbBrowser):
    session: Session
    char: Characters
    territory: Clans | None
    herb: Herbs | None

    def __init__(self, char_name: str, territory: str | None = None) -> None:
        super().__init__()
        self.char_name = char_name
        self.territory_name = territory
        self.char = self.select_one(
            select(Characters).where(Characters.name == self.char_name)
        )
        self.territory = (
            self.select_one(select(Clans).where(Clans.name == territory))
            if territory
            else None
        )
        self.herb = self.get_herb()

    def gather(self) -> tuple[Herbs | None, bool]:
        return self.herb, self.check_success()

    def get_herb(self) -> Herbs | None:
        res = roll()
        logger.debug(f"roll result for herbalism: {res}")
        query = select(Herbs).where(
            and_(
                Herbs.rarity_max >= res,
                Herbs.rarity_min <= res,
                (
                    or_(
                        Herbs.territory == None,
                        Herbs.territory
                        == (self.territory.no if self.territory else -1),
                    )
                ),
            )
        )
        with self.session as s:
            poss_herb = s.exec(query).all()
        try:
            herb = choice(poss_herb)
        except IndexError:
            herb = None
        logger.debug(f"Трава для сбора: {str(herb)}")
        return herb

    def check_success(self):
        if not self.herb:
            return False
        res = self.char.actual_stats["healing"] + self.char.actual_stats["herbalism"]
        if self.herb.sum_required > res:
            logger.debug(f"Провал собирательства: {self.char.name}, {self.herb.name}")
            return False
        logger.debug(f"Успешно собрана трава {self.char.name}, {self.herb.name}")
        return True


class HerbConfig(DbBrowser):
    session: Session

    def __init__(self) -> None:
        super().__init__()

    def add_herb(self, params: dict):
        herb = Herbs(**params)
        self.add(herb)

    def delete_herb(self, name: str):
        herb = self.get_herb_by_name(name)
        self.delete(herb)

    def get_herb_by_name(self, name: str):
        return self.select_one(select(Herbs).where(Herbs.name == name))

    def get_all_herbs(self):
        return self.select_many(select(Herbs))
    
    def get_herb_by_no(self, no: int) -> Herbs | None:
        return self.safe_select_one(select(Herbs).where(Herbs.no == no))

    def edit_herb(self, name: str, params: dict[str, str | int | None]):
        herb = self.get_herb_by_name(name.capitalize())
        for key, value in params.items():
            setattr(herb, key, value)
        self.add(herb)
