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
