from sqlmodel import select

from db import Settings, DbBrowser, Characters


class SettingConfig(DbBrowser):

    def __init__(self):
        super().__init__()
    
    def set_setting(self, name: str, value: str):
        old: Settings = self.select_one(select(Settings).where(Settings.name == name))
        old.value = value
        self.add(old)
    
    def get_setting(self, name: str):
        return self.select_one(select(Settings).where(Settings.name == name)).value()
    
    def insert_new_setting(self, params: dict[str, str]):
        return self.add(Settings(**params))

    def curr_hunger_pens(self):
        return Characters._get_hunger_pen()
    
    def get_all_settings(self):
        return self.select_many(select(Settings))