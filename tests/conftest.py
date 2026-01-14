from dataclasses import dataclass
import logging
from typing import Any, Iterable

import pytest
from sqlmodel import SQLModel, Session, func, select, create_engine

from db import DbBrowser, Players, Characters, SQLModel as Tables


@dataclass(frozen=True)
class FillData:
    player_w_2_cats = 1
    player_w_1_cat = 2
    cat_name_one_1 = 'cat_player_one'
    cat_name_one_2 = 'another_cat_player_one'
    cat_name_two_1 = 'cat_player_two'
    test_player = dict(chat_id=player_w_2_cats, username='test_player')
    test_player_2 = dict(chat_id=player_w_1_cat, username='test_player_2')
    test_cat_one_1 = dict(name=cat_name_one_1, player_chat_id=player_w_2_cats, hunting=1, age=10)
    test_cat_one_2 = dict(name=cat_name_one_2, player_chat_id=player_w_2_cats, hunting=1, age=10)
    test_cat_two = dict(name=cat_name_two_1, player_chat_id=player_w_1_cat, hunting=1, age=10)


def _create_memory_bd():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as c:
        cur = c.connection.cursor()
        cur.execute('PRAGMA foreign_keys = ON;')
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

    handler_class: type[DbBrowser]
    kwargs: dict[str, Any]

    @pytest.fixture(scope="function")
    def mock_inherit(self):
        if self.handler_class.__bases__ != ((DbBrowser,)):
            raise Exception(f"Класс {self.handler_class.__name__} унаследован не только от DbBrowser!: {self.handler_class.__bases__}")
        self.handler_class.__bases__ = (MockBrowser,)
        if self.kwargs:
            mocked = self.handler_class(**self.kwargs)
        else:
            mocked = self.handler_class()
        mocked.session.close_resets_only = False
        yield mocked
        mocked.session.rollback()
        mocked.session.close()
        self.handler_class.__bases__ = (DbBrowser,)
    
    @pytest.fixture()
    def fill_test_players(self, mock_inherit):
        handler = mock_inherit
        handler.add_many([Players(**FillData.test_player), Players(**FillData.test_player_2)])
    
    @pytest.fixture()
    def fill_test_chars(self, mock_inherit):
        handler = mock_inherit
        handler.add_many([Characters(**FillData.test_cat_one_1), Characters(**FillData.test_cat_one_2), Characters(**FillData.test_cat_two)])
    
    def compare(self, dbres: SQLModel | Iterable[SQLModel] | None, eta: SQLModel | Iterable[SQLModel] | None, pk_name: str = "no"):
        """Method to compare instanses and/or Iterables of instanses of SQLModel class disregarding any primary key fields."""

        def compare_instanse(dbres: SQLModel, eta: SQLModel):
            if dbres.__class__ != eta.__class__:
                return False
            for field_name in dbres.__class__.model_fields.keys():
                if getattr(dbres, field_name) != getattr(eta, field_name) and field_name != pk_name:
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
