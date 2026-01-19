from unittest.mock import MagicMock

from db.characters import DbCharacterConfig
from db.hunt import Hunt
from tests.conftest import FillData, BaseTest


class TestHuntNoClan(BaseTest):
    handler_class = Hunt
    kwargs = {"char_name": FillData.cat_name_one_1, "territory": 2}
    supp_classes = [DbCharacterConfig]

    class MockSeason(MagicMock):
        hunt_mod = 0
        name = "test_season"

    def test_hunt_no_clan(
        self, fill_test_players, fill_test_chars, fill_test_prey, fill_test_lands, mock_inherit, mocker
    ):
        handler = mock_inherit
        mocker.patch.object(handler, "char_config", MagicMock())
        mocker.patch.object(Hunt, "get_curr_season", return_value=self.MockSeason())
        mocker.patch.object(Hunt, "get_setting", return_value={"hunt_attempts": 1000})
        res = handler.hunt()
        print(res)
        assert res
