# -*- coding: utf-8 -*-
import logging
import time
from datetime import datetime
from telethon import types
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class kafkMod(loader.Module):
    """Предоставляет сообщение о том, что вы недоступны"""
    strings = {"name": "kafk",
               "gone": "<b>kafk включен</b>",
               "back": "<b>kafk выключен</b>",
               "kafk": "<b>Я сейчас kafk (так как {} назад).</b>",
               "kafk_reason": "<b>Я сейчас kafk (так как {} "
                             "назад).\nПричина:</b> <i>{}</i>"}

    def __init__(self):#1256285611
        self.config = loader.ModuleConfig(
            "EXCEPTION_ID", [""], "Исключения идентификаторов пользователей")

    async def client_ready(self, client, db):
        self._db = db
        self._me = await client.get_me()

    async def kafkcmd(self, message):
        """.kafk [message]"""
        if utils.get_args_raw(message):
            self._db.set(__name__, "mes", utils.get_args_raw(message))
            self._db.set(__name__, "kafk", utils.get_args_raw(message))
        else:
            self._db.set(__name__, "kafk", True)
        self._db.set(__name__, "gone", time.time())
        await self.allmodules.log("kafk", data=utils.get_args_raw(message) or None)
        await utils.answer(message, self.strings("gone", message))

    async def unkafkcmd(self, message):
        """Remove the pafk status"""
        self._db.set(__name__, "kafk", False)
        self._db.set(__name__, "gone", None)
        await self.allmodules.log("unkafk")
        await utils.answer(message, self.strings("back", message))

    async def watcher(self, message):
        if not self.get_kafk():
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


    def get_kafk(self):
        return self._db.get(__name__, "kafk", False)
