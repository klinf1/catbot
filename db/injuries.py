from sqlmodel import Session, and_, select

from db import CharacterInjury, DbBrowser, Injuries, InjuryStat


class DbInjuryCharacter(DbBrowser):
    session: Session

    def __init__(self, char_no: int, injury: int) -> None:
        super().__init__()
        self.char = char_no
        self.injury = injury

    def add_injury(self):
        inj = CharacterInjury(issue=self.injury, character=self.char)
        self.add(inj)

    def remove_injury(self):
        inj = select(CharacterInjury).where(
            CharacterInjury.issue == self.injury, CharacterInjury.character == self.char
        )
        with self.session as s:
            inj = s.exec(inj).one()
        self.delete(inj)


class DbInjuryConfigure(DbBrowser):
    session: Session

    def __init__(self) -> None:
        super().__init__()

    def get_injury_by_name(self, name: str) -> Injuries:
        query = select(Injuries).where(Injuries.name == name)
        with self.session as s:
            return s.exec(query).one()

    def add_new_injury(self, name: str, penalties: dict[str, int]):
        query_inj = Injuries(name=name)
        self.add(query_inj)
        self._add_injury_stats(name, penalties)

    def delete_injury(self, name: str | None = None):
        inj = select(Injuries).where(Injuries.name == name)
        with self.session as s:
            inj = s.exec(inj).one()
        self.delete(inj)

    def edit_injury(
        self, no: int, name: str | None = None, penalties: dict[str, int] = {}
    ):
        inj = select(Injuries).where(Injuries.no == no)
        with self.session as s:
            inj = s.exec(inj).one()
        inj.name = name if name else inj.name
        with self.session as s:
            s.add(inj)
        if penalties:
            inj_stats = select(InjuryStat.stat).where(InjuryStat.issue == inj.no)
            with self.session as s:
                inj_stats = s.exec(inj_stats).all()
            self._edit_router(no, penalties, inj_stats)

    def _edit_router(self, no: int, penalties: dict[str, int], existing_stats):
        existing_pens = [stat for stat in existing_stats]
        pen_new = {
            key: value for key, value in penalties.items() if key not in existing_pens
        }
        pens_to_edit = {
            key: value for key, value in penalties.items() if key in existing_pens
        }
        pens_to_delete = [
            stat for stat in existing_pens if stat not in penalties.keys()
        ]
        self._add_injury_stats(self.get_injury_by_no(no).name, pen_new)
        self._change_injury_stat(no, pens_to_edit)
        self._delete_injury_stats(no, pens_to_delete)

    def _change_injury_stat(self, no: int, penalties: dict[str, int]):
        for key, value in penalties.items():
            inj_stat = select(InjuryStat).where(
                and_(InjuryStat.issue == no, InjuryStat.stat == key)
            )
            with self.session as s:
                inj_stat = s.exec(inj_stat).one()
                inj_stat.penalty = value
                self.add(inj_stat)

    def _add_injury_stats(self, name: str, penalties: dict):
        inj = self.get_injury_by_name(name=name)
        for key, value in penalties.items():
            query_stat = InjuryStat(issue=inj.no, stat=key, penalty=value)  # type: ignore
            self.add(query_stat)

    def _delete_injury_stats(self, no: int, to_delete: list[str]):
        for stat in to_delete:
            query = select(InjuryStat).where(
                and_(InjuryStat.issue == no, InjuryStat.stat == stat)
            )
            with self.session as s:
                stat_to_delete = s.exec(query).one()
            self.delete(stat_to_delete)

    def get_injury_by_no(self, no: int):
        query = select(Injuries).where(Injuries.no == no)
        with self.session as s:
            return s.exec(query).one()

    def view_all_injuries(self):
        query = select(Injuries).join(InjuryStat)
        with self.session as s:
            return s.exec(query).all()
