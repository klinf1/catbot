from random import choice, randint
from sqlite3 import IntegrityError

from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, and_, exists, select

from db import Characters, Clans, DbBrowser, Prey, PreyTerritory
from db.injuries import DbInjuryCharacter
from exceptions import (CharacterDeadException, CharacterFrozenException,
                        NoItemFoundDbError)
from logs.logs import main_logger as logger
from roll import roll


class Hunt(DbBrowser):
    prey: Prey | None
    char: Characters
    clan: Clans | None
    session: Session

    def __init__(self, char_name: str, territory: str | None = None) -> None:
        super().__init__()
        self.territory = territory
        self.char_name = char_name
        self.char = self.get_char()
        self.clan = self.get_clan()
        self.prey = self.get_prey()

    def hunt(self) -> tuple[Prey | None, bool]:
        self.validate_char()
        res = self.check_success()
        if res is False:
            # self.apply_consequences()
            pass
        return self.prey, res

    def validate_char(self):
        if self.char.is_frozen:
            raise CharacterFrozenException
        if self.char.is_dead:
            raise CharacterDeadException

    def get_prey(self) -> Prey | None:
        res = roll()
        logger.debug(f"roll result for hunt: {res}")
        if self.clan:
            query = (
                select(Prey)
                .join(PreyTerritory)
                .where(
                    and_(
                        Prey.rarity <= res,
                        PreyTerritory.territory == self.clan.no,
                    )
                ),
            )
            poss_prey = self.select_many(query)
        else:
            poss_prey = []
            prey_list_q = select(Prey).where(
                exists(select(PreyTerritory).where(PreyTerritory.prey == Prey.no))
                == False
            )
            prey_list = self.select_many(prey_list_q)
            for p in prey_list:
                if p.rarity_max >= res and p.rarity_min <= res:
                    poss_prey.append(p)
        try:
            prey = choice(poss_prey)
        except IndexError:
            prey = None
        logger.debug(f"Дичь для охоты: {str(prey)}")
        return prey

    def get_char(self) -> Characters:
        query = select(Characters).where(Characters.name == self.char_name)
        try:
            res = self.select_one(query)
        except NoResultFound as err:
            raise NoItemFoundDbError(f"Персонаж {self.char_name} не найден.") from err
        return res

    def get_clan(self) -> Clans | None:
        logger.debug(f"Getting cat territory for {self.territory}")
        if not self.territory:
            return None
        try:
            query = select(Clans).where(Clans.name == self.territory.capitalize())
            return self.select_one(query)
        except NoResultFound as err:
            raise NoItemFoundDbError(f"Клан {self.territory} не найден.") from err

    def check_success(self) -> bool:
        if not self.prey:
            return False
        stat = self.prey.stat.lower()
        res = self.char.actual_stats["hunting"] + self.char.actual_stats[stat]
        if self.prey.territory == self.char.clan_no:
            res += self.char.actual_stats["faith"]
        logger.debug(f"Результат охоты: {res} против {self.prey.sum_required or 0}")
        if (self.prey.sum_required or 0) > res:
            logger.debug(f"Охота провалилась {self.prey.sum_required or 0} > {res}")
            return False
        logger.debug(f"Охота успешна {self.prey.sum_required or 0} <= {res}")
        return True

    def apply_consequences(self) -> None:
        if (
            self.prey.injury_chance
            and randint(1, 100) < self.prey.injury_chance
            and self.prey.injury
        ):
            logger.debug(f"{self.char.name} получает ранение {self.prey.injury}")
            try:
                DbInjuryCharacter(self.char.no, self.prey.injury).add_injury()
            except IntegrityError as err:
                logger.debug(
                    f"Повторное ранение {self.prey.injury} для {self.char.name}, игнорирую"
                )
