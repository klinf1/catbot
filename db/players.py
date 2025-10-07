from sqlmodel import Session, and_, select

from db import Characters, DbBrowser, Players
from db.characters import DbCharacterConfig


class DbPlayerConfig(DbBrowser):
    session: Session

    def __init__(self) -> None:
        super().__init__()

    def add_player(
        self,
        chat_id: int,
        username: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ):
        new_player = Players(
            chat_id=chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        self.add(new_player)

    def ban_player(self, username: str):
        query = select(Players).where(Players.username == username)
        with self.session as s:
            player = s.exec(query).one()
        if not player.is_superuser and not player.is_admin:
            player.is_banned = True
            self.add(player)
            query = select(Characters).where(
                Characters.player_chat_id == player.chat_id
            )
            with self.session as s:
                for cat in s.exec(query).all():
                    DbCharacterConfig().edit_freeze_char_by_no(cat.no, True)
            return f"Игрок {username} забанен успешно."
        else:
            return "Не нужно пытаться банить админов!"

    def unban_player(self, username: str):
        query = select(Players).where(
            and_(Players.username == username, Players.is_banned == True)
        )
        try:
            with self.session as s:
                player = s.exec(query).one()
        except Exception as e:
            print(e)
            return
        player.is_banned = False
        self.add(player)
        query = select(Characters).where(Characters.player_chat_id == player.chat_id)
        with self.session as s:
            for cat in s.exec(query).all():
                DbCharacterConfig().edit_freeze_char_by_no(cat.no, False)
        return f"Игрок {username} разбанен."

    def check_if_user_is_admin(self, chat_id) -> bool:
        query = select(Players).where(Players.chat_id == chat_id)
        with self.session as s:
            player = s.exec(query).one()
        if player.is_admin or player.is_superuser:
            return True
        return False

    def get_player_by_username(self, username: str):
        query = select(Players).where(Players.username == username)
        with self.session as s:
            player = s.exec(query).one()
        return player

    def promote_or_demote(self, username: str, flag: bool):
        query = select(Players).where(Players.username == username)
        with self.session as s:
            player = s.exec(query).one()
        player.is_admin = flag
        self.add(player)

    def get_all_players(self):
        query = select(Players)
        with self.session as s:
            players = s.exec(query).all()
        return players
