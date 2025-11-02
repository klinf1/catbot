from sqlmodel import Session, and_, select

from db import Characters, DbBrowser, Players
from db.characters import DbCharacterConfig


class DbPlayerConfig(DbBrowser):
    session: Session

    def __init__(self, admin: str | None = "") -> None:
        super().__init__()
        self.admin = admin
        self.player_config = DbCharacterConfig(admin)

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

    def ban_player(self, username: str) -> tuple[bool, str]:
        query = select(Players).where(Players.username == username)
        player: Players = self.safe_select_one(query)
        if not player:
            return False, 'Игрок с таким именем не найден!'
        if not player.is_superuser and not player.is_admin:
            player.is_banned = True
            self.add(player)
            query = select(Characters).where(
                Characters.player_chat_id == player.chat_id
            )
            with self.session as s:
                for cat in s.exec(query).all():
                    self.player_config.edit_freeze_char_by_no(cat.no, True)
            return True, f"Игрок {username} забанен успешно."
        else:
            return False, "Не нужно пытаться банить админов!"

    def unban_player(self, username: str) -> tuple[bool, str]:
        query = select(Players).where(
            and_(Players.username == username, Players.is_banned == True)  #noqa: E712
        )
        player: Players = self.safe_select_one(query)
        if not player:
            return False, 'Забаненный игрок с таким именем не найден!'
        player.is_banned = False
        self.add(player)
        query = select(Characters).where(Characters.player_chat_id == player.chat_id)
        with self.session as s:
            for cat in s.exec(query).all():
                self.player_config.edit_freeze_char_by_no(cat.no, False)
        return True, f"Игрок {username} разбанен."

    def check_if_user_is_admin(self, chat_id) -> bool:
        query = select(Players).where(Players.chat_id == chat_id)
        with self.session as s:
            player = s.exec(query).one()
        if player.is_admin or player.is_superuser:
            return True
        return False

    def get_player_by_username(self, username: str) -> Players | None:
        query = select(Players).where(Players.username == username)
        return self.safe_select_one(query)

    def promote_or_demote(self, username: str, flag: bool) -> tuple[bool, str]:
        query = select(Players).where(Players.username == username, Players.is_banned == False)  #noqa: E712
        player: Players = self.safe_select_one(query)
        if not player:
            return False, 'Игрок с таким именем не найден!'
        player.is_admin = flag
        self.add(player)
        return True, f'Игрок {username} {"повышен" if flag is True else "уволен"} успешно'

    def get_all_players(self) -> list[Players]:
        query = select(Players)
        return self.select_many(query)
    
    def get_player_by_id(self, chat_id: int) -> Players | None:
        query = select(Players).where(Players.chat_id == chat_id)
        return self.safe_select_one(query)

    def get_all_banned(self) -> list[Players]:
        query = select(Players).where(Players.is_banned == True)  #noqa: E712
        return self.select_many(query)
