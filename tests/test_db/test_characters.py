import pytest

from db import Characters
from db.characters import DbCharacterUser, DbCharacterConfig
from tests.conftest import FillData, BaseTest


class CharacterBase(BaseTest):

    @pytest.fixture(scope="function")
    def setup_test_data(self, mock_inherit):
        handler = mock_inherit
        handler.add_many([FillData.test_player, FillData.test_player_2])        
        handler.add_many([FillData.test_cat_one_1, FillData.test_cat_one_2, FillData.test_cat_two])
        yield handler
        

class TestUser(CharacterBase):

    handler_class = DbCharacterUser
    kwargs = {"chat_id": FillData.player_w_2_cats}

    def test_getting_all(self, mock_inherit, fill_test_players, fill_test_chars):
        handler: DbCharacterUser = mock_inherit
        res = handler.get_all_own_chars()
        assert self.compare(res, [Characters(**FillData.test_cat_one_1), Characters(**FillData.test_cat_one_2)])
        
    def test_getting_name(self, mock_inherit, fill_test_players, fill_test_chars):
        handler: DbCharacterUser = mock_inherit
        res = handler.get_one_own_char(FillData.cat_name_one_1)
        assert self.compare(res, Characters(**FillData.test_cat_one_1))


class TestConfig(CharacterBase):

    handler_class = DbCharacterConfig
    kwargs = {"admin": "tests"}

    def test_get_char_by_name(self, mock_inherit, fill_test_players, fill_test_chars):
        handler: DbCharacterConfig = mock_inherit
        res = handler.get_char_by_name(FillData.cat_name_one_1)
        assert self.compare(res, Characters(**FillData.test_cat_one_1))
    
    def test_get_char_by_no(self, mock_inherit, fill_test_players, fill_test_chars, last_char_no):
        handler: DbCharacterConfig = mock_inherit
        res = handler.get_char_by_no(last_char_no+1)
        assert self.compare(res, Characters(**FillData.test_cat_one_1))
    
    def test_get_chars_for_player(self, mock_inherit, fill_test_players, fill_test_chars):
        handler = mock_inherit
        res = handler.get_chars_for_player(FillData.player_w_2_cats)
        assert self.compare(res, [Characters(**FillData.test_cat_one_1), Characters(**FillData.test_cat_one_2)])
    
    # TODO: test additional failure points
    @pytest.mark.parametrize('params, good', [({"name": "juja", "age": 10, "player_chat_id": 1}, True),
                                              ({"name": FillData.cat_name_one_1, "age": 10, "player_chat_id": 1}, False),
                                              ({}, False),
                                              ])
    def test_add_character(self, mock_inherit, fill_test_players, fill_test_chars, params, good):
        handler = mock_inherit
        if not good:
            with pytest.raises(Exception):
                handler.add_character(params)
        else:
            handler.add_character(params)
            exists = handler.get_char_by_name(params["name"])
            assert exists
            assert exists.age == params["age"]
            assert exists.player_chat_id == params["player_chat_id"]
            assert exists.hunting == params.get("hunting", 0)
    
    def test_edit_character(self, mock_inherit, fill_test_players, fill_test_chars):
        handler = mock_inherit
        new_val = 5
        handler.edit_character(FillData.cat_name_one_1, {"hunting": new_val}, "test")
        res = handler.get_char_by_name(FillData.cat_name_one_1)
        assert res.hunting == new_val
        hist = handler.get_char_history(FillData.cat_name_one_1)
        assert hist, "Ошибка записи в историю!"
        assert len(hist) == 1
        assert hist[0].reason == "test"
        assert hist[0].user == self.kwargs["admin"]
        assert hist[0].field == "hunting"
        assert hist[0].old == "1"
        assert hist[0].new == str(new_val)
    
    def test_delete_character(self, mock_inherit, fill_test_players, fill_test_chars):
        handler = mock_inherit
        char = handler.get_char_by_name(FillData.cat_name_one_1)
        handler.delete_character_by_no(char.no)
        assert handler.get_char_by_name(FillData.cat_name_one_1) is None
    
    @pytest.mark.parametrize("flag", [(True), (False)])
    def test_freeze_character(self, mock_inherit, fill_test_players, fill_test_chars, flag):
        handler = mock_inherit
        handler.edit_freeze_char_by_name(FillData.cat_name_one_1, "test", flag)
        res = handler.get_char_by_name(FillData.cat_name_one_1)
        assert res.is_frozen == flag
    
    @pytest.mark.parametrize("flag", [(True), (False)])
    def test_death_character(self, mock_inherit, fill_test_players, fill_test_chars, flag):
        handler = mock_inherit
        handler.edit_death_char_by_name(FillData.cat_name_one_1, "test", flag)
        res = handler.get_char_by_name(FillData.cat_name_one_1)
        assert res.is_dead == flag