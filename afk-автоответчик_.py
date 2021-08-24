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
        # await utils.answer(message, self.strings("back", message))

    async def watcher(self, message):
        if not self.get_afk():
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
                        return
            except Exception as e:
                return

        now = datetime.now().replace(microsecond=0)
        gone = datetime.fromtimestamp(self._db.get(__name__, "gone")).replace(microsecond=0)
        diff = now - gone

        if getattr(message.to_id, "user_id", None) == self._me.id:
            if not self.get_afk():
                return
            afk_state = self._db.get(__name__, "afks", '...')
            ret = self.strings("afk_reason", message).format(diff, afk_state)
            await utils.answer(message, ret)

        elif message.mentioned:
            if self.get_afk():
                afk_state = self._db.get(__name__, "afks", '...')
                ret = self.strings("afk_reason", message).format(diff, afk_state)
                await utils.answer(message, ret, reply_to=message)
            else:
                return

    def get_afk(self):
        return self._db.get(__name__, "afk", False)
