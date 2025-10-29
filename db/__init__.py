from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar

from pydantic import computed_field, field_validator
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlmodel import (CheckConstraint, Column, Field, Integer,
                      Session, SQLModel, UniqueConstraint, and_, create_engine,
                      select)
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar
from db.table_data import AGES, CLANS, SEASONS, SETTINGS
from logs.logs import main_logger as logger

engine = create_engine("sqlite:///cats.db")
as_engine = create_async_engine("sqlite+aiosqlite:///cats.db")


class Buffs(SQLModel, table=True):
    """
    Table for any buffs the cats might receive.

    :var str name:
    """

    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str


class BuffsStats(SQLModel, table=True):
    """
    Table to link buffs to their attributes.

    :var int buff: foreign key to buffs.no
    :var str stat: stat affected
    :var int>0 increase: value of stat change
    """

    no: int | None = Field(primary_key=True, default=None)
    buff: int = Field(foreign_key="buffs.no", ondelete="CASCADE")
    stat: str
    increase: int = Field(sa_column=Column(Integer))
    __table_args__ = (CheckConstraint(increase.sa_column > 0),)


class Notifications(SQLModel, table=True):
    """
    Table for various pre-determined text messages to users.

    :var str entity: The object that is referenced e.g. a prey type
    :var str entity_action: The action taken e.g. hunt_successful
    :var str text: Text to be sent
    """

    no: int | None = Field(primary_key=True, default=None)
    entity: str
    entity_action: str
    text: str


class CharacterBuffs(SQLModel, table=True):
    """
    Table to link buffs to characters.

    :var int buff: Foreign key to buffs.no
    :var int character: Foreign key to characters.no
    """

    __table_args__ = (UniqueConstraint("buff", "character", name="unique_buff"),)
    no: int | None = Field(primary_key=True, default=None)
    buff: int = Field(foreign_key="buffs.no", ondelete="CASCADE")
    character: int = Field(foreign_key="characters.no", ondelete="CASCADE")


class Players(SQLModel, table=True):
    """
    Table of all active players.

    :var int chat_id: telegram chat id.
    :var str username: telegram username.
    :var bool is_admin:
    :var bool is_superuser:
    :var bool is_banned:
    :var str|None=None first_name: telegram first name.
    :var str|None=None last_name: telegram last name.
    """

    __table_args__ = (UniqueConstraint("chat_id", name="player_chatid_unique"),)
    no: int | None = Field(primary_key=True, default=None, index=True)
    chat_id: int
    username: str
    is_admin: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    is_banned: bool = Field(default=False)
    first_name: str | None = None
    last_name: str | None = None

    def __str__(self) -> str:
        return (
            f"Id: {self.no}\nИгрок: {self.chat_id}\nUsername: {self.username}\nFirst name: {self.first_name}\nLast name: {self.last_name}"
            f"\nЗабанен: {'Да' if self.is_banned else 'Нет'}\nАдмин: {'Да' if self.is_admin else 'Нет'}\nСуперюзер: {'Да' if self.is_superuser else 'Нет'}"
        )


class Seasons(SQLModel, table=True):
    """
    Table with season info.

    :var str name:
    :var int hunt_mod:
    :var bool=False is_active:
    """

    __table_args__ = (UniqueConstraint("name", name="seasons_name_unique"),)
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str = Field(index=True)
    hunt_mod: int
    herb_mod: int
    is_active: bool = False
    next: str

    @staticmethod
    def attrs():
        return ['name', 'hunt_mod', 'herb_mod', 'next']
    
    def __str__(self):
        return "\n".join(
            [
                f"Название: {self.name}",
                f"Модификатор охоты: {self.hunt_mod}",
                f"Модификатор травничества: {self.herb_mod}",
                f"Следующий сезон: {self.next}",
            ]
        )


class Clans(SQLModel, table=True):
    """
    Table with clans info.

    :var str name:
    :var int|None leader: current leader, foreign key to characters.no
    """

    __table_args__ = (UniqueConstraint("name", name="clans_name_unique"),)
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str = Field(index=True)
    leader: int | None = Field(default=None, nullable=True)
    is_true_clan: bool = Field(default=False, nullable=False)

    @staticmethod
    def attrs():
        return [ "is_true_clan"]
    
    def prey_pile(self):
        res = 0
        query = select(Prey).join(PreyPile, onclause= PreyPile.prey == Prey.no).where(PreyPile.clan == self.no)
        with Session(engine) as s:
            all_prey = s.exec(query).all()
        for item in all_prey:
            res += item.amount
        return res

    def __str__(self):
        leader = select(Characters).where(Characters.no == self.leader)
        prey = (
            select(Prey).join(PreyTerritory).where(PreyTerritory.territory == self.no)
        )
        with Session(engine) as s:
            leader = s.exec(leader).first()
            prey = s.exec(prey).all()
        fields = [
            f"Id: {self.no}",
            f"Тип: {'Клан' if self.is_true_clan else 'Территория'}",
            f"Название: {self.name}",
            f"Дичь: {', '.join([prey.name for prey in prey])}",
        ]
        if self.is_true_clan:
            fields += [
                f"Текущee количество запасов: {self.prey_pile()}",
                f"Лидер: {leader.name if leader else 'отсутствует'}",
            ]
        return "\n".join(fields)


class HerbPile(SQLModel, table=True):
    """
    Table with clan's herb pile info.

    :var int clan: foreign_key to clans.no
    :var int herb: foreign key to herbs.no
    """

    no: int | None = Field(primary_key=True, default=None, index=True)
    clan: int | None = Field(default=None, foreign_key="clans.no", ondelete="CASCADE")
    herb: int | None = Field(default=None, foreign_key="herbs.no", ondelete="CASCADE")


class Herbs(SQLModel, table=True):
    """
    Table with herb info.

    :var name str:
    :var rarity_min int: min roll amount to find this herb
    :var rarity_max int: max roll amount to find this herb
    :var int disease: disease to be treated by this herb, foreign key to diseases.no
    :var int injury: injury to be treated by this herb, foreign key to injuries.no
    """

    __table_args__ = (UniqueConstraint("name", name="herbs_name_unique"),)
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str = Field(index=True)
    territory: int | None = Field(
        foreign_key="clans.no", default=None, ondelete="SET NULL"
    )
    sum_required: int = 0
    rarity_min: int
    rarity_max: int
    disease: int | None = Field(
        foreign_key="diseases.no", default=None, ondelete="SET NULL"
    )
    injury: int | None = Field(
        foreign_key="injuries.no", default=None, ondelete="SET NULL"
    )

    @staticmethod
    def attrs():
        return [
            "territory",
            "rarity_min",
            "rarity_max",
            "disease",
            "injury",
            "sum_required",
        ]

    @property
    def clan(self):
        query = select(Clans).where(Clans.no == self.territory)
        with Session(engine) as s:
            clans = s.exec(query).one()
        return clans

    @property
    def actual_disease(self):
        query = select(Diseases).where(Diseases.no == self.disease)
        with Session(engine) as s:
            return s.exec(query).one()

    @property
    def actual_injury(self):
        query = select(Injuries).where(Injuries.no == self.injury)
        with Session(engine) as s:
            return s.exec(query).one()

    def __str__(self) -> str:
        if not self.territory:
            terr = "любая"
        elif self.territory == -1:
            terr = "нейтральная"
        else:
            terr = self.clan.name
        if not self.disease:
            disease = "нет"
        else:
            disease = self.actual_disease.name
        if not self.injury:
            injury = "нет"
        else:
            injury = self.actual_injury.name
        return "\n".join(
            [
                f"Id: {self.no}Название: {self.name}",
                f"Территория происхождения: {terr}",
                f"Минимальная редкость: {self.rarity_min}",
                f"Максимальная редкость: {self.rarity_max}",
                f"Болезнь: {disease}",
                f"Трама: {injury}",
            ]
        )


class CharacterInventory(SQLModel, table=True):
    """
    Table for prey in character inventory.

    :var int char_no: foreign key to characters.no
    :var str type: what is this - herb or prey
    :var int item: no from prey or herbs that is in this inventory
    """

    no: int | None = Field(primary_key=True, default=None, index=True)
    char_no: int = Field(foreign_key="characters.no", ondelete="CASCADE")
    type: str
    item: int
    
    @field_validator("type")
    @classmethod
    def check_type(cls, v: Any):
        if v not in ["prey", "herb"]:
            raise ValueError("Тип содержимого может быть только prey | herb!")
        return v


class Roles(SQLModel, table=True):
    """
    Table for roles in clans.

    :var str name:
    :var bool is_senior:
    """

    __table_args__ = (UniqueConstraint("name", name="roles_name_unique"),)
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str = Field(index=True)
    is_senior: bool = False
    food_required: int


class Injuries(SQLModel, table=True):
    """
    Table for injuries.

    :var str name:
    """

    __table_args__ = (UniqueConstraint("name", name="injuries_name_unique"),)
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str


class CharacterInjury(SQLModel, table=True):
    """
    Table to link characters and injuries.

    :var int issue: foreign key to injuries.no
    :var int issue: foreign key to characters.no
    """

    __table_args__ = (UniqueConstraint("issue", "character", name="unique_injury"),)
    no: int | None = Field(primary_key=True, default=None)
    issue: int = Field(foreign_key="injuries.no", ondelete="CASCADE")
    character: int = Field(foreign_key="characters.no", ondelete="CASCADE")


class InjuryStat(SQLModel, table=True):
    """
    Table to link injuries and characters.

    :var int issue: foreign key to injuries.no
    :var str stat: stat affected
    :var int<0 penalty: value substracted
    """

    no: int | None = Field(primary_key=True, default=None)
    issue: int = Field(foreign_key="injuries.no", ondelete="CASCADE")
    stat: str
    penalty: int = Field(sa_column=Column(Integer))
    __table_args__ = (CheckConstraint(penalty.sa_column < 0),)

    @staticmethod
    def attrs():
        return [
            "hunting",
            "agility",
            "hearing",
            "smell",
            "sight",
            "speed",
            "stamina",
            "strength",
            "combat",
        ]


class Diseases(SQLModel, table=True):
    """
    Table with diseases.

    :var str name:
    """

    __table_args__ = (UniqueConstraint("name", name="diseases_name_unique"),)
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str = Field(index=True)


class CharacterDisease(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("issue", "character", name="unique_disease"),)
    no: int | None = Field(primary_key=True, default=None)
    issue: int = Field(foreign_key="diseases.no", ondelete="CASCADE")
    character: int = Field(foreign_key="characters.no", ondelete="CASCADE")


class DiseaseStat(SQLModel, table=True):
    no: int | None = Field(primary_key=True, default=None)
    issue: int = Field(foreign_key="diseases.no", ondelete="CASCADE")
    stat: str
    penalty: int = Field(sa_column=Column(Integer))
    __table_args__ = (CheckConstraint(penalty.sa_column < 0),)


class Disabilities(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("name", name="disabilities_name_unique"),)
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str = Field(index=True)


class CharacterDisability(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("issue", "character", name="unique_trauma"),)
    no: int | None = Field(primary_key=True, default=None)
    issue: int = Field(foreign_key="disabilities.no", ondelete="CASCADE")
    character: int = Field(foreign_key="characters.no", ondelete="CASCADE")


class DisabilityStat(SQLModel, table=True):
    no: int | None = Field(primary_key=True, default=None)
    issue: int = Field(foreign_key="disabilities.no", ondelete="CASCADE")
    stat: str
    penalty: int = Field(sa_column=Column(Integer))
    __table_args__ = (CheckConstraint(penalty.sa_column < 0),)


class Characters(SQLModel, table=True):
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str = Field(index=True)
    player_chat_id: int = Field(foreign_key="players.chat_id", ondelete="CASCADE")
    hunting: int = Field(default=0, sa_column=Column(Integer, default=0))
    agility: int = Field(default=0, sa_column=Column(Integer, default=0))  # Agility
    hearing: int = Field(default=0, sa_column=Column(Integer, default=0))  # Hearing
    smell: int = Field(default=0, sa_column=Column(Integer, default=0))  # Smell
    sight: int = Field(default=0, sa_column=Column(Integer, default=0))  # Sight
    speed: int = Field(default=0, sa_column=Column(Integer, default=0))
    stamina: int = Field(default=0, sa_column=Column(Integer, default=0))
    strength: int = Field(default=0, sa_column=Column(Integer, default=0))
    combat: int = Field(default=0, sa_column=Column(Integer, default=0))
    herbalism: int = Field(default=0, sa_column=Column(Integer, default=0))
    healing: int = Field(default=0, sa_column=Column(Integer, default=0))
    faith: int = Field(default=0, sa_column=Column(Integer, default=0))
    role: int | None = Field(default=None, foreign_key="roles.no", ondelete="SET NULL")
    clan_no: int | None = Field(
        default=None, foreign_key="clans.no", ondelete="SET NULL"
    )
    hunger: int = 0
    nutrition: int = Field(sa_column=Column(Integer, default=0))
    age: int
    is_frozen: bool = False
    is_dead: bool = False
    curr_hunts: int = 0
    curr_herbs: int = 0
    hunger_pen: ClassVar[dict[int, int]] = {}
    __table_args__ = (
        UniqueConstraint("name", name="characters_name_unique"),
        CheckConstraint(stamina.sa_column >= 0),
        CheckConstraint(stamina.sa_column <= 10),
        CheckConstraint(hunting.sa_column >= 0),
        CheckConstraint(hunting.sa_column <= 10),
        CheckConstraint(agility.sa_column >= 0),
        CheckConstraint(agility.sa_column <= 10),
        CheckConstraint(hearing.sa_column >= 0),
        CheckConstraint(hearing.sa_column <= 10),
        CheckConstraint(smell.sa_column >= 0),
        CheckConstraint(smell.sa_column <= 10),
        CheckConstraint(sight.sa_column >= 0),
        CheckConstraint(sight.sa_column <= 10),
        CheckConstraint(speed.sa_column >= 0),
        CheckConstraint(speed.sa_column <= 10),
        CheckConstraint(strength.sa_column >= 0),
        CheckConstraint(strength.sa_column <= 10),
        CheckConstraint(combat.sa_column >= 0),
        CheckConstraint(combat.sa_column <= 10),
        CheckConstraint(herbalism.sa_column >= 0),
        CheckConstraint(herbalism.sa_column <= 10),
        CheckConstraint(healing.sa_column >= 0),
        CheckConstraint(healing.sa_column <= 10),
        CheckConstraint(faith.sa_column >= 0),
        CheckConstraint(faith.sa_column <= 10),
    )
    
    @property
    def session(self):
        return Session(engine)

    @property
    def injuries(self) -> list:
        query = select(CharacterInjury).where(CharacterInjury.character == self.no)
        return [t for t in self.session.exec(query).all()]

    @property
    def traumas(self) -> list:
        query = select(CharacterDisability).where(
            CharacterDisability.character == self.no
        )
        with self.session:
            traumas = [t for t in self.session.exec(query).all()]
        return traumas

    @property
    def diseases(self) -> list:
        query = select(CharacterDisease).where(CharacterDisease.character == self.no)
        return [t for t in self.session.exec(query).all()]

    @computed_field
    @property
    def actual_stats(self) -> dict[str, int]:
        logger.debug(f"Получены актуальные характеристики для {self.name}")
        return {
            "hunting": self.get_actual_stat("hunting"),
            "agility": self.get_actual_stat("agility"),
            "hearing": self.get_actual_stat("hearing"),
            "smell": self.get_actual_stat("hearing"),
            "sight": self.get_actual_stat("sight"),
            "speed": self.get_actual_stat("speed"),
            "stamina": self.get_actual_stat("stamina"),
            "strength": self.get_actual_stat("strength"),
            "combat": self.get_actual_stat("combat"),
            "herbalism": self.get_actual_stat("herbalism"),
            "healing": self.get_actual_stat("healing"),
            "faith": self.get_actual_stat("faith"),
        }
    
    @staticmethod
    def _get_hunger_pen() -> dict[int, int]:
        query = select(Settings).where(Settings.name.contains("hunger_pen", autoescape=True))
        with Session(engine) as s:
            res: list[Settings] = s.exec(query).all()
        hunger = {}
        for i in res:
            hunger[int(i.name.split("_")[-1])] = int(i.value)
        return hunger

    def get_actual_stat(self, stat: str) -> int:
        res = self.__getattribute__(stat)
        res += self.get_buffs(stat)
        res += self.get_penalties(stat)
        if not self.hunger_pen:
            Characters.hunger_pen = self._get_hunger_pen()
        res -= self.hunger_pen.get(self.hunger, self.hunger)
        return res

    def get_buffs(self, stat: str) -> int:
        # res = self.__getattribute__(stat)
        res = 0
        query = (
            select(BuffsStats)
            .join(CharacterBuffs, onclause=BuffsStats.buff == CharacterBuffs.buff)  # type: ignore
            .where(and_(CharacterBuffs.character == self.no, BuffsStats.stat == stat))
        )
        with self.session as s:
            buff = s.exec(query).all()
        for i in buff:
            res += i.increase
        return res

    def get_penalties(self, stat: str) -> int:
        res = 0
        table_list = [
            [InjuryStat, CharacterInjury],
            [DisabilityStat, CharacterDisability],
            [DiseaseStat, CharacterDisease],
        ]
        for cls_group in table_list:
            query = (
                select(cls_group[0])
                .join(
                    cls_group[1],
                    onclause=cls_group[0].issue == cls_group[1].issue,  # type: ignore
                )
                .where(
                    and_(cls_group[1].character == self.no, cls_group[0].stat == stat)
                )
            )
            with self.session as s:
                pen = s.exec(query).all()
            for i in pen:
                res += i.penalty
        return res

    @staticmethod
    def attrs():
        return [
            "player_chat_id*",
            "hunting",
            "agility",
            "hearing",
            "smell",
            "sight",
            "speed",
            "stamina",
            "strength",
            "combat",
            "herbalism",
            "healing",
            "faith",
            "role",
            "clan_no",
            "age*",
        ]

    @property
    def clan(self):
        query = select(Clans).where(Clans.no == self.clan_no)
        with Session(engine) as s:
            clans = s.exec(query).one()
        return clans

    @property
    def role_whole(self):
        query = select(Roles).where(Roles.no == self.role)
        with Session(engine) as s:
            role = s.exec(query).one()
        return role

    def __str__(self) -> str:
        if self.is_dead is True:
            return f"{self.name}: мертв."
        if not self.clan_no:
            clan = "бродяга"
        else:
            clan = self.clan.name
        if not self.role:
            role = "нет"
        else:
            role = self.role_whole.name
        return (
            f"Id: {self.no}\nИмя: {self.name}\nВозраст: {self.age} лун\nАктуальные характеристики:\n{'\n'.join([f'{key}: {value}' for key, value in self.actual_stats.items()])}"
            f"\nКлан: {clan}\nРоль: {role}\nСтепень голода: {self.hunger}\nЗаморожен: {'да' if self.is_frozen else 'нет'}"
        )


class PreyTerritory(SQLModel, table=True):
    no: int | None = Field(primary_key=True, default=None, index=True)
    prey: int = Field(foreign_key="prey.no", ondelete="CASCADE")
    territory: int = Field(foreign_key="clans.no", ondelete="CASCADE")


class Prey(SQLModel, table=True):
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str = Field(index=True)
    stat: str
    amount: int
    rarity: int = Field(sa_column=Column(Integer, nullable=False))
    sum_required: int = Field(sa_column=Column(Integer, nullable=False))
    injury: int | None = Field(
        default=None, foreign_key="injuries.no", ondelete="SET NULL"
    )
    injury_chance: int = Field(default=0, sa_column=Column(Integer, default=0))
    __table_args__ = (
        UniqueConstraint("name", name="prey_name_unique"),
        CheckConstraint(injury_chance.sa_column >= 0),
        CheckConstraint(injury_chance.sa_column <= 100),
        CheckConstraint(sum_required.sa_column >= 0),
        CheckConstraint(rarity.sa_column > 0),
        CheckConstraint(rarity.sa_column <= 100),
    )

    @staticmethod
    def attrs():
        return [
            "stat*",
            "amount*",
            "rarity",
            "sum_required*",
            "territory",
            "injury",
            "injury_chance",
        ]

    @property
    def injury_whole(self):
        query = select(Injuries).where(Injuries.no == self.injury)
        with Session(engine) as s:
            inj = s.exec(query).one()
        return inj

    @property
    def territory(self):
        query = select(Clans).join(PreyTerritory).where(PreyTerritory.prey == self.no)
        with Session(engine) as s:
            return s.exec(query).all()

    def __str__(self) -> str:
        if not self.territory:
            clan_name = "все"
        else:
            clan_name = ", ".join([clan.name for clan in self.territory])
        if self.injury:
            inj = self.injury_whole.name
        else:
            inj = "нет"
        return (
            f"Id: {self.no}\nНазвание: {self.name}\nНавык: {self.stat}\nПитательность: {self.amount}\nРедкость: {self.rarity}"
            f"\n\nНеобходимая сумма очков: {self.sum_required}\n"
            f"Территория проживания: {clan_name}\nНаносимое ранение: {inj}\nШанс ранения: {self.injury_chance or 'нет'}"
        )


class PreyPile(SQLModel, table=True):
    no: int | None = Field(primary_key=True, default=None, index=True)
    clan: int = Field(foreign_key="clans.no", ondelete="CASCADE")
    prey: int = Field(foreign_key="prey.no", ondelete='CASCADE')
    date_added: datetime = Field(default=datetime.now())


class Ages(SQLModel, table=True):
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str
    max_age: int
    food_req: int
    next: str | None = None

    @staticmethod
    def attrs():
        return ['name', 'max_age', 'food_req']

    def __str__(self):
        return "\n".join(
            [
                f"Название: {self.name}",
                f"Верхняя граница: {self.max_age}",
                f"Необходимое количество еды: {self.food_req}"
            ]
        )


class Settings(SQLModel, table=True):
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str
    value: str
    __table_args__ = (
        UniqueConstraint("name", name="setting_name_unique"),
    )

    def __str__(self):
        return "\n".join(
            [
                f"Название: {self.name}",
                f"Значение: {self.value}"
            ]
        )


class DbBrowser:
    def __init__(self) -> None:
        self.session = Session(engine, expire_on_commit=False)
        self.async_session = AsyncSession(as_engine)

    def commit(self):
        self.session.commit()

    def add(self, table):
        with self.session as s:
            s.add(table)
            self.commit()
    
    async def as_add(self, table: type[SQLModel]):
        async with self.async_session as s:
            s.add(table)
            await s.commit()

    def delete(self, table):
        with self.session as s:
            s.delete(table)
            self.commit()
    
    async def as_delete(self, table: type[SQLModel]):
        async with self.async_session as s:
            s.delete(table)
            await s.commit()

    def select_one(self, query: SelectOfScalar) -> type[SQLModel]:
        with self.session as s:
            return s.exec(query).one()
    
    async def as_select_one(self, query: SelectOfScalar) -> type[SQLModel]:
        async with self.async_session as s:
            res = await s.exec(query)
            return res.one()

    def select_many(self, query: SelectOfScalar):
        with self.session as s:
            return s.exec(query).all()
        
    async def as_select_many(self, query: SelectOfScalar):
        async with self.async_session as s:
            res = await s.exec(query)
            return res.all()

    def safe_select_one(self, query: SelectOfScalar) -> type[SQLModel] | None:
        with self.session as s:
            return s.exec(query).first()
    
    async def as_safe_select_one(self, query: SelectOfScalar) -> type[SQLModel] | None:
        async with self.async_session as s:
            res = await s.exec(query)
            return res.first()
    
    def fill_default(self) -> None:
        if not self.select_many(select(Ages)):
            for i in AGES:
                self.add(Ages(**i))
        if not self.select_many(select(Seasons)):
            for i in SEASONS:
                self.add(Seasons(**i))
        if not self.select_many(select(Clans)):
            for i in CLANS:
                self.add(Clans(**i))
        if not self.select_many(select(Settings)):
            for i in SETTINGS:
                self.add(Settings(**i))
        return None
    
    def add_admins(self, ids: list[str], usernames: list[str]):
        for id, username in zip(ids, usernames):
            username = username.replace("'", "")
            with self.session as s:
                query = select(Players).where(Players.chat_id == int(id))
                if not s.exec(query).all():
                    admin = Players(
                        chat_id=int(id),
                        username=username,
                        is_admin=True,
                        is_superuser=True,
                    )
                    self.add(admin)


def create_tables() -> None:
    """Created baseline tables if they do not exist already."""
    with engine.connect() as c:
        cur = c.connection.cursor()
        cur.execute('PRAGMA foreign_keys = ON;')
    SQLModel.metadata.create_all(engine)
    DbBrowser().fill_default()
