 # -*- coding: utf-8 -*-
import logging
import time
from datetime import datetime
from telethon import types
from .. import loader, utils
import asyncio

logger = logging.getLogger(__name__)


@loader.tds
class pafkMod(loader.Module):
    """Предоставляет сообщение о том, что вы недоступны"""
    strings = {"name": "pafk",
               "gone": "<b>pafk включен</b>",
               "back": "<b>pafk выключен</b>",
               "pafk": "<b>Я сейчас pafk (так как {} назад).</b>",
               "pafk_reason": "<b>Я сейчас pafk (так как {} "
                             "назад).\nПричина:</b> <i>{}</i>"}

    def __init__(self):#1256285611
        self.config = loader.ModuleConfig(
            "EXCEPTION_ID", [""], "Исключения идентификаторов пользователей")

    async def client_ready(self, client, db):
        self._db = db
        self._me = await client.get_me()

    async def pafkcmd(self, message):
        """.pafk [message]"""
        if utils.get_args_raw(message):
            self._db.set(__name__, "mes", utils.get_args_raw(message))
            self._db.set(__name__, "pafk", utils.get_args_raw(message))
        else:
            self._db.set(__name__, "pafk", True)
        self._db.set(__name__, "gone", time.time())
        self._db.set(__name__, "ratelimit", [])
        await self.allmodules.log("pafk", data=utils.get_args_raw(message) or None)
        await utils.answer(message, self.strings("gone", message))
        await asyncio sleep(1)
        await message.delete()

        

    async def unpafkcmd(self, message):
        """Remove the pafk status"""
        self._db.set(__name__, "pafk", False)
        self._db.set(__name__, "gone", None)
        self._db.set(__name__, "ratelimit", [])
        await self.allmodules.log("unpafk")
        await utils.answer(message, self.strings("back", message))
        await asyncio sleep(1)
        await message.delete()

    async def watcher(self, message):
        if not isinstance(message, types.Message):
            return
        if not isinstance(message, types.Message):
            return
        if message.mentioned or getatpafk(message.to_id, "user_id", None) == self._me.id:
            pafk_state = self.get_pafk()
            if not pafk_state:
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
            if self.get_pafk() is False:
                return
        if not self.get_pafk():
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
                    if text == text:
                        mes = self._db.get(__name__, "mes", False)
                        if mes:
                            await message.client.send_message(message.chat_id, mes ,reply_to=message.id)
            except Exception as e:
                pass

    def get_pafk(self):
        return self._db.get(__name__, "pafk", False)
