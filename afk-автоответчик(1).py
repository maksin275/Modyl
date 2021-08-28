# -*- coding: utf-8 -*-
import logging
import time
from datetime import datetime
from telethon import types
from .. import loader, utils
import asyncio

logger = logging.getLogger(__name__)


@loader.tds
class trMod(loader.Module):
    """Предоставляет сообщение о том, что вы недоступны"""
    strings = {"name": "Автоответчик",
               "gone": "<b>Автоответчик включен</b>",
               "back": "<b>Автоответчик выключен</b>",
               "tr": "<b>Я сейчас tr (так как {} назад).</b>",
               "tr_reason": "<b>Я сейчас tr (так как {} "
                             "назад).\nПричина:</b> <i>{}</i>"}

    def __init__(self):#1256285611
        self.config = loader.ModuleConfig(
            "EXCEPTION_ID", [""], "Исключения идентификаторов пользователей")

    async def client_ready(self, client, db):
        self._db = db
        self._me = await client.get_me()

    async def trcmd(self, message):
        """.tr [message]"""
        await asyncio.sleep(5)
        if utils.get_args_raw(message):
            self._db.set(__name__, "mes", utils.get_args_raw(message))
            self._db.set(__name__, "tr", utils.get_args_raw(message))
        else:
            self._db.set(__name__, "tr", True)
        self._db.set(__name__, "gone", time.time())
        await self.allmodules.log("tr", data=utils.get_args_raw(message) or None)
        await utils.answer(message, self.strings("gone", message))

    async def untrcmd(self, message):
        """Remove the tr status"""
        self._db.set(__name__, "tr", False)
        self._db.set(__name__, "gone", None)
        await self.allmodules.log("untr")
        await utils.answer(message, self.strings("back", message))

    async def watcher(self, message):
        if not self.get_tr():
            return
        if getattr(message, "sender_id", None):
            if str(message.sender_id) in self.config["EXCEPTION_ID"]:
                return
        if not isinstance(message, types.Message):
            return

        if getattr(message.peer_id, "user_id", None):
            if message.out:
                return
            try:
                a = await message.client.get_entity(message.chat_id)
                if a.bot:
                    return
                else:
                    text = message.text
                    if text == '+':
                        mes = self._db.get(__name__, "mes", False)
                        if mes:
                            await message.client.send_message(message.chat_id, mes ,reply_to=message.id)
            except Exception as e:
                pass


    def get_tr(self):
        return self._db.get(__name__, "tr", False)
