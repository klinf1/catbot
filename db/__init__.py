from pydantic import computed_field
from sqlmodel import (CheckConstraint, Column, Field, Integer, Session,
                      SQLModel, UniqueConstraint, and_, create_engine, func,
                      select)

engine = create_engine("sqlite:///cats.db")


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
    buff: int = Field(foreign_key="buffs.no")
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
    buff: int = Field(foreign_key="buffs.no")
    character: int = Field(foreign_key="characters.no")


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


class Seasons(SQLModel, table=True):
    """
    Table with season info.

    :var str name:
    :var int hunt_attemps:
    :var bool=False is_active:
    """

    __table_args__ = (UniqueConstraint("name", name="seasons_name_unique"),)
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str = Field(index=True)
    hunt_attempts: int
    is_active: bool = False


class Clans(SQLModel, table=True):
    """
    Table with clans info.

    :var str name:
    :var int prey_pile_percent: amount of prey in clan's pile
    :var int|None leader: current leader, foreign key to characters.no
    """

    __table_args__ = (UniqueConstraint("name", name="clans_name_unique"),)
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str = Field(index=True)
    prey_pile_percent: int = 0
    leader: int | None = Field(foreign_key="characters.no", default=None)

    @staticmethod
    def attrs():
        return ["prey_pile_percent"]


class HerbPile(SQLModel, table=True):
    """
    Table with clan's herb pile info.

    :var int clan: foreign_key to clans.no
    :var int herb: foreign key to herbs.no
    """

    no: int | None = Field(primary_key=True, default=None, index=True)
    clan: int | None = Field(default=None, foreign_key="clans.no")
    herb: int | None = Field(default=None, foreign_key="herbs.no")


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
    rarity_min: int
    rarity_max: int
    disease: int | None = Field(foreign_key="diseases.no", default=None)
    injury: int | None = Field(foreign_key="injuries.no", default=None)


class CharacterInventory(SQLModel, table=True):
    """
    Table for prey in character inventory.

    :var int char_no: foreign key to characters.no
    :var int slot_one: foreign key to prey.no
    :var int slot_two: foreign key to prey.no
    :var int slot_three: foreign key to prey.no
    """

    no: int | None = Field(primary_key=True, default=None, index=True)
    char_no: int | None = Field(foreign_key="characters.no", default=None)
    slot_one: int | None = Field(foreign_key="prey.no", default=None)
    slot_two: int | None = Field(foreign_key="prey.no", default=None)
    slot_three: int | None = Field(foreign_key="prey.no", default=None)


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
    issue: int = Field(foreign_key="injuries.no")
    character: int = Field(foreign_key="characters.no")


class InjuryStat(SQLModel, table=True):
    """
    Table to link injuries and characters.

    :var int issue: foreign key to injuries.no
    :var str stat: stat affected
    :var int<0 penalty: value substracted
    """

    no: int | None = Field(primary_key=True, default=None)
    issue: int = Field(foreign_key="injuries.no")
    stat: str
    penalty: int = Field(sa_column=Column(Integer))
    __table_args__ = (CheckConstraint(penalty.sa_column < 0),)


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
    issue: int = Field(foreign_key="diseases.no")
    character: int = Field(foreign_key="characters.no")


class DiseaseStat(SQLModel, table=True):
    no: int | None = Field(primary_key=True, default=None)
    issue: int = Field(foreign_key="diseases.no")
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
    issue: int = Field(foreign_key="disabilities.no")
    character: int = Field(foreign_key="characters.no")


class DisabilityStat(SQLModel, table=True):
    no: int | None = Field(primary_key=True, default=None)
    issue: int = Field(foreign_key="disabilities.no")
    stat: str
    penalty: int = Field(sa_column=Column(Integer))
    __table_args__ = (CheckConstraint(penalty.sa_column < 0),)


class Characters(SQLModel, table=True):
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str = Field(index=True)
    player_chat_id: int | None = Field(foreign_key="players.chat_id", default=None)
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
    role: int | None = Field(default=None, foreign_key="roles.no")
    clan_no: int | None = Field(default=None, foreign_key="clans.no")
    hunger: int = 0
    has_eaten: bool = True
    is_frozen: bool = False
    is_dead: bool = False
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

    @computed_field
    @property
    def injuries(self) -> list:
        query = select(CharacterInjury).where(CharacterInjury.character == self.no)
        return [t for t in self.session.exec(query).all()]

    @computed_field
    @property
    def traumas(self) -> list:
        query = select(CharacterDisability).where(
            CharacterDisability.character == self.no
        )
        with self.session:
            traumas = [t for t in self.session.exec(query).all()]
        return traumas

    @computed_field
    @property
    def diseases(self) -> list:
        query = select(CharacterDisease).where(CharacterDisease.character == self.no)
        return [t for t in self.session.exec(query).all()]

    @computed_field
    @property
    def actual_stats(self) -> dict[str, int]:
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

    def get_actual_stat(self, stat: str) -> int:
        res = self.__getattribute__(stat)
        res += self.get_buffs(stat)
        res += self.get_penalties(stat)
        res -= self.hunger
        return res if res > 0 else 0

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
            "player_chat_id",
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
            return "Мертв."
        if not self.clan_no:
            clan = "бродяга"
        else:
            clan = self.clan.name
        if not self.role:
            role = "нет"
        else:
            role = self.role_whole.name
        return (
            f"Имя: {self.name}\nАктуальные характеристики: {', '.join([f'{key}: {value}' for key, value in self.actual_stats.items()])}"
            f"\nКлан: {clan}\nРоль: {role}\nСтепень голода: {self.hunger}\nЗаморожен: {'да' if self.is_frozen else 'нет'}"
        )


class Prey(SQLModel, table=True):
    no: int | None = Field(primary_key=True, default=None, index=True)
    name: str = Field(index=True)
    stat: str
    amount: int
    rarity_min: int
    rarity_max: int
    sum_required: int = Field(sa_column=Column(Integer))
    territory: int | None = None
    injury: int | None = Field(default=None, foreign_key="injuries.no")
    injury_chance: int = Field(default=0, sa_column=Column(Integer, default=0))
    __table_args__ = (
        UniqueConstraint("name", name="prey_name_unique"),
        CheckConstraint(injury_chance.sa_column >= 0),
        CheckConstraint(injury_chance.sa_column <= 100),
        CheckConstraint(sum_required.sa_column >= 0),
    )

    @staticmethod
    def attrs():
        return [
            "stat",
            "amount",
            "rarity_min",
            "rarity_max",
            "sum_required",
            "territory",
            "injury",
            "injury_chance",
        ]

    @property
    def clan(self):
        query = select(Clans).where(Clans.no == self.territory)
        with Session(engine) as s:
            clan = s.exec(query).one()
        return clan

    @property
    def injury_whole(self):
        query = select(Injuries).where(Injuries.no == self.injury)
        with Session(engine) as s:
            inj = s.exec(query).one()
        return inj

    def __str__(self) -> str:
        if self.territory == -1:
            clan_name = "территория двуногихсе"
        elif not self.territory:
            clan_name = "все"
        else:
            clan_name = self.clan.name
        if self.injury:
            inj = self.injury_whole.name
        else:
            inj = "нет"
        return (
            f"Название: {self.name}\nНавык: {self.stat}\nПитательность: {self.amount}\nМинимальный бросок: {self.rarity_min}"
            f"\nМаксимальный бросок: {self.rarity_max}\nНеобходимая сумма очков: {self.sum_required}\n"
            f"Территория проживания: {clan_name}\nНаносимое ранение: {inj}\nШанс ранения: {self.injury_chance or 'нет'}"
        )


class DbBrowser:
    def __init__(self) -> None:
        self.session = Session(engine)

    def commit(self):
        self.session.commit()

    @property
    def max_prey(self):
        query = select(func.count()).select_from(Prey)
        with self.session as s:
            return s.exec(query).one()

    def add(self, table):
        with self.session as s:
            s.add(table)
            self.commit()

    def delete(self, table):
        with self.session as s:
            s.delete(table)
            self.commit()


def create_tables() -> None:
    """Created baseline tables if they do not exist already."""

    SQLModel.metadata.create_all(engine)


class AtStart(DbBrowser):
    def __init__(self) -> None:
        super().__init__()

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
