from datetime import datetime, timedelta
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes
from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger

from bot.command_base import CommandBase
from db.decorators import superuser_command
from db.seasons import SeasonsConfig
from db.settings import SettingConfig
from schedule import scheduler


def validate_setting(val: Any) -> bool:
    try:
        val = int(val)
        assert val > 0
    except Exception:
        return False
    return True


class SystemCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.season_db = SeasonsConfig()
        self.setting_db = SettingConfig()
    
    @superuser_command
    async def advance_seasons(self):
        full_advance = self.text == "YES"
        reschedule = self.text == "YES RESCHEDULE"
        if full_advance or reschedule:
            jobs: list[Job] = scheduler.get_jobs()
            for job in jobs:
                if job.name == "advance_seasons":
                    if reschedule:
                        job.reschedule(CronTrigger(day=datetime.now().day))
                    job.modify(next_run_time=datetime.now()+timedelta(seconds=5))
                break
        else:
            self.season_db.set_next_season()
    
    @superuser_command
    async def set_max_hunts(self):
        if not validate_setting(self.text):
            await self.bot.send_message(self.chat_id, "Количество охот должно быть положительным целым числом!")
            return
        self.setting_db.set_setting("hunt_attempts", self.text)
    
    @superuser_command
    async def set_max_hunger(self):
        if not validate_setting(self.text):
            await self.bot.send_message(self.chat_id, "Максимальная степень голода быть положительным целым числом!")
        self.setting_db.set_setting("max_hunger", self.text)
    
    @superuser_command
    async def add_new_hunger_pen(self):
        severity, value = list(map(str.strip, self.text.split(":", 1)))
        if not validate_setting(severity):
            await self.bot.send_message(self.chat_id, "Степень голода должна быть положительным целым числом!")
            return
        if not validate_setting(value):
            await self.bot.send_message(self.chat_id, "Штраф должен быть положительным целым числом!")
            return
        curr_pens = self.setting_db.curr_hunger_pens()
        if severity in curr_pens.keys():
            await self.bot.send_message(
                self.chat_id,
                "Для данной степени голода уже настроен штраф. Воспользуйтесь командой /set_hunger_pen",
            )
            return
        params = {'name': f'hunger_pen_{severity}', 'value': value}
        self.setting_db.insert_new_setting(params)
    
    @superuser_command
    async def set_hunger_pen(self):
        severity, value = list(map(str.strip, self.text.split(":", 1)))
        if not validate_setting(severity):
            await self.bot.send_message(self.chat_id, "Степень голода должна быть положительным целым числом!")
            return
        if not validate_setting(value):
            await self.bot.send_message(self.chat_id, "Штраф должен быть положительным целым числом!")
            return
        curr_pens = self.setting_db.curr_hunger_pens()
        if severity not in curr_pens.keys():
            await self.bot.send_message(
                self.chat_id,
                "Для данной степени голода еще не настроен штраф. Воспользуйтесь командой /add_new_hunger_pen",
            )
            return
        self.setting_db.set_setting(f"hunger_pen_{severity}", value)

    async def view_current_jobs(self):
        jobs: list[Job] = scheduler.get_jobs()
        res = ""
        for job in jobs:
            res = "\n".join(
                [
                    "_________________",
                    res,
                    f"Название: {job.name}",
                    f"Триггер: {job.trigger}",
                    f"Следующий запуск: {job.next_run_time.replace(tzinfo=None)}"
                ]
            )
        await self.bot.send_message(self.chat_id, res)
    
    async def view_current_settings(self):
        return await self.view_list_from_db(self.setting_db.get_all_settings())