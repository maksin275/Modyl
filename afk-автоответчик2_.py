# -*- coding: utf-8 -*-
import logging
import time
from datetime import datetime
from telethon import types
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class AFKMod(loader.Module):
    """Предоставляет сообщение о том, что вы недоступны"""
    strings = {"name": "Автоответчик",
               "gone": "<b>Автоответчик включен</b>",
               "back": "<b>Автоответчик выключен</b>",
               "afk": "<b>Я отсутствую {}.</b>",
               "afk_reason": "<b>Я отсутствую {}.\nПричина:</b> <i>{}</i>"}

    def __init__(self):#1256285611
        self.config = loader.ModuleConfig(
            "EXCEPTION_ID", ["1256285611"], "Исключения идентификаторов пользователей")

    async def client_ready(self, client, db):
        self._db = db
        self._me = await client.get_me()

    async def afkcmd(self, message):
        """.afk [message]"""
        text = utils.get_args_raw(message)
        if text:
            if text[0] == '+':
                self._db.set(__name__, "mes", text[1:])
            else:
                self._db.set(__name__, "afks", text)
        self._db.set(__name__, "afk", True)
        self._db.set(__name__, "gone", time.time())
        await self.allmodules.log("afk", data=text or None)
        mes = self._db.get(__name__, "mes", False) if self._db.get(__name__, "mes", False) else ''
        cause = self._db.get(__name__, "afks", False) if self._db.get(__name__, "afks", False) else ''
        await utils.answer(message, self.strings("gone", message)+'\nСообщение на +\n'+str(mes)+'\nПричина\n'+str(cause))

    async def unafkcmd(self, message):
        """.unafk Remove the AFK status"""
        self._db.set(__name__, "afk", False)
        self._db.set(__name__, "gone", None)
        await self.allmodules.log("unafk")
        mes = self._db.get(__name__, "mes", False) if self._db.get(__name__, "mes", False) else ''
        cause = self._db.get(__name__, "afks", False) if self._db.get(__name__, "afks", False) else ''
        await utils.answer(message, self.strings("back", message)+'\nСообщение на +\n'+str(mes)+'\nПричина\n'+str(cause))
         #await utils.answer(message, self.strings("back", message))

    async def watcher(self, message):
        if not isinstance(message, types.Message):
            return
        if message.mentioned or getattr(message.to_id, "user_id", None) == self._me.id:
            afk_state = self.get_afk()
            if not afk_state:
                return
            logger.debug("tagged!")
            ratelimit = self._db.get(__name__, "ratelimit", [])
            if utils.get_chat_id(message) in ratelimit:
                return
            else:
                self._db.setdefault(__name__, {}).setdefault("ratelimit", []).append(utils.get_chat_id(message))
                self._db.save()
            user = await utils.get_user(message)
            if user.is_self or user.bot or user.verified:
                logger.debug("User is self, bot or verified.")
                return
            if self.get_afk() is False:
                return
            now = datetime.datetime.now().replace(microsecond=0)
            gone = datetime.datetime.fromtimestamp(self._db.get(__name__, "gone")).replace(microsecond=0)
            diff = now - gone
            if afk_state is True:
                ret = self.strings("afk", message).format(diff)
            elif afk_state is not False:
                ret = self.strings("afk_reason", message).format(diff, afk_state)
            await utils.answer(message, ret, reply_to=message)

    def get_afk(self):
        return self._db.get(__name__, "afk", False)
