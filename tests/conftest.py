from dataclasses import dataclass
import logging
from typing import Any, Iterable

import pytest
from sqlmodel import SQLModel, Session, func, select, create_engine

from db import Clans, DbBrowser, Players, Characters, Prey, PreyTerritory, SQLModel as Tables


@dataclass(frozen=True)
class FillData:
    player_w_2_cats = 1
    player_w_1_cat = 2
    cat_name_one_1 = "Cat_player_one"
    cat_name_one_2 = "Another_cat_player_one"
    cat_name_two_1 = "Cat_player_two"
    players = [
        dict(chat_id=player_w_2_cats, username="test_player"),
        dict(chat_id=player_w_1_cat, username="test_player_2"),
    ]
    cats = [
        dict(name=cat_name_one_1, player_chat_id=player_w_2_cats, hunting=1, age=10),
        dict(name=cat_name_one_2, player_chat_id=player_w_2_cats, hunting=1, age=10),
        dict(name=cat_name_two_1, player_chat_id=player_w_1_cat, hunting=1, age=10),
    ]
    test_player = dict(chat_id=player_w_2_cats, username="test_player")
    test_player_2 = dict(chat_id=player_w_1_cat, username="test_player_2")
    test_cat_one_1 = dict(name=cat_name_one_1, player_chat_id=player_w_2_cats, hunting=1, age=10)
    test_cat_one_2 = dict(name=cat_name_one_2, player_chat_id=player_w_2_cats, hunting=1, age=10)
    test_cat_two = dict(name=cat_name_two_1, player_chat_id=player_w_1_cat, hunting=10, age=10)
    prey = [
        dict(name="Test_prey_ez", stat="agility", amount="1", rarity=100, sum_required=1),
        dict(name="Test_prey_hard", stat="agility", amount="1", rarity=100, sum_required=5),
    ]
    clan_prey = [
        dict(name="Test_prey_ez_c", stat="agility", amount="1", rarity=100, sum_required=1),
        dict(name="Test_prey_hard_c", stat="agility", amount="1", rarity=100, sum_required=5),
    ]
    clan = dict(name="Test_clan", is_true_clan=True)
    terr = dict(name="Test_terr")


engine = create_engine("sqlite:///:memory:")


def _create_memory_bd():
    with engine.connect() as c:
        cur = c.connection.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")
    Tables.metadata.create_all(engine)
    return engine


class MockBrowser(DbBrowser):
    def __init__(self):
        self.session = Session(_create_memory_bd())

    def add(self, table):
        self.session.add(table)
        self.session.flush()

    def delete(self, table):
        self.session.delete(table)
        self.session.flush()
        FillData.test_cat_one_1

    def add_many(self, val):
        for i in val:
            self.session.add(i)
        self.session.flush()

    def delete_many(self, val) -> None:
        for i in val:
            self.session.add(i)
        self.session.flush()

    def commit(self):
        self.session.flush()

    def select_one(self, query):
        return self.session.exec(query).one()

    def select_many(self, query):
        return self.session.exec(query).all()

    def safe_select_one(self, query):
        return self.session.exec(query).first()


class BaseTest:
    handler_class: type[DbBrowser] | Iterable[type[DbBrowser]]
    kwargs: dict[str, Any]
    supp_classes: Iterable[type[DbBrowser]] | None = None

    @pytest.fixture(scope="function")
    def mock_inherit(self, mocker):
        mocker.patch("db.engine", engine)
        prev_bases = self.handler_class.__bases__
        self.handler_class.__bases__ = (MockBrowser,)
        if self.supp_classes:
            for i in self.supp_classes:
                i.__bases__ = (MockBrowser,)
        if self.kwargs:
            mocked = self.handler_class(**self.kwargs)
        else:
            mocked = self.handler_class()
        mocked.session.close_resets_only = False
        yield mocked
        mocked.session.rollback()
        mocked.session.close()
        self.handler_class.__bases__ = prev_bases
        if self.supp_classes:
            for i in self.supp_classes:
                i.__bases__ = (DbBrowser,)

    @pytest.fixture()
    def fill_test_players(self, mock_inherit):
        handler = mock_inherit
        for i in FillData.players:
            handler.add(Players(**i))

    @pytest.fixture()
    def fill_test_chars(self, mock_inherit):
        handler = mock_inherit
        for i in FillData.cats:
            handler.add(Characters(**i))

    @pytest.fixture()
    def fill_test_prey(self, mock_inherit):
        handler = mock_inherit
        for i in FillData.prey:
            handler.add(Prey(**i))

    @pytest.fixture()
    def fill_test_lands(self, mock_inherit):
        handler = mock_inherit
        for i in [FillData.clan, FillData.terr]:
            handler.add(Clans(**i))

    @pytest.fixture()
    def fill_prey_terr(self, mock_inherit):
        handler = mock_inherit
        for i in FillData.clan_prey:
            handler.add(Prey(**i))
        handler.add(PreyTerritory(prey=3, territory=1))
        handler.add(PreyTerritory(prey=4, territory=2))

    def compare(
        self,
        dbres: SQLModel | Iterable[SQLModel] | None,
        eta: SQLModel | Iterable[SQLModel] | None,
    ):
        """Method to compare instanses and/or Iterables of instanses of SQLModel class disregarding any primary key fields."""

        def compare_instanse(dbres: SQLModel, eta: SQLModel):
            if dbres.__class__ != eta.__class__:
                return False
            for field_name, field_info in dbres.__class__.model_fields.items():
                if getattr(dbres, field_name) != getattr(eta, field_name) and not field_info.primary_key:
                    return False
            return True

        if dbres == eta:
            return True
        elif isinstance(dbres, SQLModel) and isinstance(dbres, SQLModel):
            return compare_instanse(dbres, eta)
        elif isinstance(dbres, Iterable) and isinstance(eta, Iterable):
            if len(dbres) != len(eta):
                return False
            for i in list(zip(dbres, eta)):
                if compare_instanse(i[0], i[1]) is False:
                    return False
            else:
                return True
        else:
            return False


@pytest.fixture()
def last_char_no():
    res = MockBrowser().safe_select_one(select(func.max(Characters.no)))
    if res is None:
        return 0
    return res


@pytest.fixture(scope="function", autouse=True)
def mock_log(mocker):
    mocker.patch("logs.logs.set_up_logger", side_effect=logging.getLogger)
