from typing import Any

from telegram import Update
from telegram.ext import ContextTypes
from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger

from bot.buttons import get_job_keyboard
from bot.command_base import CommandBase, CallbackBase
from db.decorators import superuser_command
from db.seasons import SeasonsConfig
from db.settings import SettingConfig
from logs.logs import system_logger as logger
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
    
    @property
    def jobs(self) -> list[Job]:
        return scheduler.get_jobs()
    
    @superuser_command
    async def advance_seasons(self):
        logger.info(f"Advancing seasons {self.user.username}")
        self.season_db.set_next_season()
    
    @superuser_command
    async def set_max_hunts(self):
        if not self.validate_setting(self.text):
            await self.bot.send_message(self.chat_id, "Количество охот должно быть положительным целым числом!")
            return
        logger.info(f"hunt_attempts change to {self.text} {self.user.username}")
        self.setting_db.set_setting("hunt_attempts", self.text)
    
    @superuser_command
    async def set_max_hunger(self):
        if not self.validate_setting(self.text):
            await self.bot.send_message(self.chat_id, "Максимальная степень голода должна быть положительным целым числом!")
            return
        logger.info(f"max_hunger change to {self.text} {self.user.username}")
        self.setting_db.set_setting("max_hunger", self.text)
    
    @superuser_command
    async def add_new_hunger_pen(self):
        severity, value = list(map(str.strip, self.text.split(":", 1)))
        if not self.validate_setting(severity):
            await self.bot.send_message(self.chat_id, "Степень голода должна быть положительным целым числом!")
            return
        if not self.validate_setting(value):
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
        logger.info(f"new hunger_pen_{severity} {value} for {self.user.username}")
        self.setting_db.insert_new_setting(params)
    
    @superuser_command
    async def set_hunger_pen(self):
        severity, value = list(map(str.strip, self.text.split(":", 1)))
        if not self.validate_setting(severity):
            await self.bot.send_message(self.chat_id, "Степень голода должна быть положительным целым числом!")
            return
        if not self.validate_setting(value):
            await self.bot.send_message(self.chat_id, "Штраф должен быть положительным целым числом!")
            return
        curr_pens = self.setting_db.curr_hunger_pens()
        if severity not in curr_pens.keys():
            await self.bot.send_message(
                self.chat_id,
                "Для данной степени голода еще не настроен штраф. Воспользуйтесь командой /add_new_hunger_pen",
            )
            return
        logger.info(f"update hunger_pen_{severity} {value} for {self.user.username}")
        self.setting_db.set_setting(f"hunger_pen_{severity}", value)

    async def view_current_jobs(self):
        res = ""
        for job in self.jobs:
            job_str = f"Название: {job.name}\nТриггер: {job.trigger}\nId: {job.id}\nСледующий запуск: {job.next_run_time.replace(tzinfo=None)}"
            res = "\n".join(
                [
                    res,
                    job_str,
                    "_________________",
                ]
            )
        await self.bot.send_message(self.chat_id, res)
    
    async def view_current_settings(self):
        return await self.view_list_from_db(self.setting_db.get_all_settings())

    @superuser_command
    async def modify_job(self):
        text = "Эта комманда позволяет менять параметры запуска джоба. Будьте КРАЙНЕ осторожны с ее использованием."
        self.context.user_data.update({"state": {"name": "settings", "action": "view_modify"}})
        logger.info(f"modify_job call for {self.user.username}")
        await self.bot.send_message(self.chat_id, text, reply_markup=get_job_keyboard(self.jobs))
    
    @superuser_command
    async def run_job(self):
        for job in self.jobs:
            if job.name.lower() == self.text.lower():
                logger.info(f"run_job {job.name} call for {self.user.username}")
                job.func()
                break
        else:
            self.bot.send_message(self.chat_id, "Джоба с таким названием не существует")
    
    @superuser_command
    async def set_max_age(self):
        if not self.validate_setting(self.text):
            await self.bot.send_message(self.chat_id, "Максимальный возраст должен быть положительным целым числом!")
        self.setting_db.set_setting("max_age", self.text)

class SystemConv(CallbackBase):

    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
    
    async def route_conv(self):
        if not (state := self.context.user_data.get("state")):
            return None
        match state.get("action"):
            case "view_modify":
                job_id = self.update.callback_query.data
                job: Job = scheduler.get_job(job_id)
                text = "\n".join([f"Выбран джоб {job.name}. Сейчас он запускается {job.trigger}",
                                  "Для редактирования джоба в следующем сообщении введите параметры триггера",
                                  "Правила можно посмотреть в документации:",
                                  "https://docs.google.com/spreadsheets/d/1X3CUqSVVF1FrHxGJyhlO8QApehsUR5AnN9oqJJSl_K0/edit?gid=0#gid=0"])
                self.context.user_data.update({"state": {"name": "settings", "action": "set_trigger", "id": job.id}})
                logger.info(f"modify_job chosen job {job.name} for {self.user.username}")
                await self.bot.send_message(self.chat_id, text)


class SystemTextCommand:
    
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.update = update
        self.context = context
        self.job_id: str = context.user_data["state"]["id"]
    
    async def job_modify(self):
        job: Job = scheduler.get_job(self.job_id)
        params_list = self.update.message.text.strip().split(";")
        params = {}
        for param in params_list:
            param = param.strip()
            k, v = param.split("=")
            params.update({k: v})
        job = job.modify(trigger=CronTrigger(**params))
        self.context.user_data.__delitem__("state")
        logger.info(f"modify_job params {params} for {self.update.message.from_user.username}")
        await self.context.bot.send_message(self.update.effective_chat.id, f"Джоб {job.name} изменен успешно")
