from sqlmodel import and_, select

from db import CharacterInventory, DbBrowser, Session


class InventoryManager(DbBrowser):
    session: Session

    def __init__(self) -> None:
        super().__init__()

    def get_char_inventory(self, char_no: int):
        query = select(CharacterInventory).where(CharacterInventory.char_no == char_no)
        return self.select_many(query)

    def add_item(self, char_no: int, type: str, item_id: int) -> str:
        item = CharacterInventory(char_no=char_no, type=type, item=item_id)
        if len(self.get_char_inventory(char_no)) >= 3:
            return "В инвентаре персонажа не может быть больше 3 предметов."
        else:
            self.add(item)
            return "Предмет успешно добавлен в инвентарь персонажа."

    def remove_item(self, char_no: int, item_id: int) -> bool:
        query = select(CharacterInventory).where(
            and_(
                CharacterInventory.char_no == char_no,
                CharacterInventory.item == item_id,
            )
        )
        item = self.safe_select_one(query)
        if item:
            self.delete(item)
            return True
        else:
            return False

    def clear_inventory(self, char_no: int) -> bool:
        query = select(CharacterInventory).where(CharacterInventory.char_no == char_no)
        items = self.select_many(query)
        if items:
            for item in items:
                self.delete(item)
            return True
        else:
            return False
