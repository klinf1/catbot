from sqlmodel import Session, select

from db import Seasons, DbBrowser


class SeasonsConfig(DbBrowser):
    session: Session

    def __init__(self):
        super().__init__()
    
    def set_next_season(self) -> None:
        query_curr = select(Seasons).where(Seasons.is_active == True)  #noqa: E712
        curr_season: Seasons = self.select_one(query_curr)
        query_next = select(Seasons).where(Seasons.name == curr_season.next)
        next_season: Seasons = self.select_one(query_next)
        curr_season.is_active = False
        next_season.is_active = True
        self.add(curr_season)
        self.add(next_season)
        return None
    
    def get_season(self, season: str | int | Seasons):
        if isinstance(season, str):
            season = self.safe_select_one(select(Seasons).where(Seasons.name == season))
        if isinstance(season, int):
            season = self.safe_select_one(select(Seasons).where(Seasons.no == season))
        return season
    
    def get_all_seasons(self):
        return self.select_many(select(Seasons))
    
    def add_season(self, params: dict):
        return self.add(Seasons(**params))
    
    def remove_season(self, season: int | str | Seasons):
        season = self.get_season(season)
        return self.delete(season)
    
    def edit_season(self, season: int | str | Seasons, params: dict):
        season - self.get_season(season)
        for i in Seasons.attrs():
            if i in params.values():
                setattr(season, i, params[i])
        self.add(season)
    
    def get_active_season(self):
        return self.select_one(select(Seasons).where(Seasons.is_active == True))  # noqa: E712


