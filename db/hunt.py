from random import choice, randint
from sqlite3 import IntegrityError

from sqlmodel import Session, and_, select

from db import Characters, Clans, DbBrowser, Prey, PreyTerritory, Seasons, Settings
from db.characters import DbCharacterConfig
from db.injuries import DbInjuryCharacter
from exceptions import (CharacterDeadException, CharacterFrozenException,
                        NoItemFoundDbError, TooMuchHuntingError)
from logs.logs import main_logger as logger
from roll import roll


class Hunt(DbBrowser):
    prey: Prey | None
    char: Characters
    clan: Clans | None
    session: Session

    def __init__(self, char_name: str, territory: str) -> None:
        super().__init__()
        self.territory = territory.strip().capitalize()
        self.char_name = char_name.strip().capitalize()
        self.char = self.get_char()
        self.clan = self.get_clan()
        self.prey = self.get_prey()
        self.settings = self.get_settings()
        self.char_config = DbCharacterConfig()

    def hunt(self) -> tuple[Prey | None, bool]:
        self.validate_char()
        res = self.check_success()
        self.char_config.edit_character(self.char.name, {"curr_hunts": self.char.curr_hunts+1})
        if res is False:
            # self.apply_consequences()
            pass
        return self.prey, res
    
    def get_settings(self) -> dict:
        query = select(Settings).where(Settings.area == "hunt")
        settings: list[Settings] = self.select_many(query)
        return {"hunt_attempts": i.value for i in settings if i.name == "hunt_attempts" or 0}

    def validate_char(self):
        if self.char.is_frozen:
            raise CharacterFrozenException
        if self.char.is_dead:
            raise CharacterDeadException
        if self.char.curr_hunts >= self.settings.get("hunt_attempts"):
            raise TooMuchHuntingError

    def get_prey(self) -> Prey | None:
        res = roll()
        logger.debug(f"roll result for hunt: {res}")
        season_q = select(Seasons).where(Seasons.is_active == True)  # noqa: E712
        season: Seasons = self.safe_select_one(season_q)
        if not season:
            mod = 0
        else:
            mod = season.hunt_mod
        query = (
            select(Prey)
            .join(PreyTerritory)
            .where(
                and_(
                    Prey.rarity + mod >= res,
                    PreyTerritory.territory == self.clan.no,
                )
            )
        )
        poss_prey = self.select_many(query)
        try:
            prey = choice(poss_prey)
        except IndexError:
            prey = None
        logger.debug(f"Дичь для охоты: {str(prey)}")
        return prey

    def get_char(self) -> Characters:
        logger.debug(f'getting char data for name {self.char_name}')
        query = select(Characters).where(Characters.name == self.char_name)
        res = self.safe_select_one(query)
        if not res:
            raise NoItemFoundDbError(f"Персонаж {self.char_name} не найден.")
        return res

    def get_clan(self) -> Clans:
        logger.debug(f"Getting cat territory for {self.territory}")
        query = select(Clans).where(Clans.name == self.territory)
        res = self.safe_select_one(query)
        if not res:
            raise NoItemFoundDbError(f"Клан {self.territory} не найден.")
        return res

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
            except IntegrityError:
                logger.debug(
                    f"Повторное ранение {self.prey.injury} для {self.char.name}, игнорирую"
                )
