from sqlmodel import select

from db import Ages, DbBrowser


class AgeConfig(DbBrowser):

    def __init__(self):
        super().__init__()
    
    def get_ages(self):
        return self.select_many(select(Ages))
    
    def new_age(self, params: dict):
        return self.add(Ages(**params))
    
    def edit_food_req(self, name: str, food_req: int):
        age: Ages | None = self.safe_select_one(select(Ages).where(Ages.name == name))
        if age:
            age.food_req = food_req
            self.add(age)
            return age
        else:
            return "Возраста с таким названием не найдено!"
