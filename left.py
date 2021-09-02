# -*- coding: utf-8 -*-

# Module author: @ftgmodulesbyfl1yd
import asyncio
from .. import loader, utils


@loader.tds
class leftMod(loader.Module):
	"""Прощание пользователей в чате."""
	strings = {'name': 'Left'}

	async def client_ready(self, client, db):
		self.db = db
		self.client = client

	async def leftcmd(self, message):
		"""Включить/выключить Прощание новых пользователей в чате.
		Используй: .left <clearall (по желанию)>. """
		left = self.db.get("left", "left", {})
		chatid = str(message.chat_id)
		args = utils.get_args_raw(message)
		if args == "clearall":
			self.db.set("left", "left", {})
			return await message.edit("<b>[left Mode]</b> Все настройки "
			                          "модуля сброшены.")

		if chatid in left:
			left.pop(chatid)
			self.db.set("left", "left", left)
			return await message.edit("<b>[left Mode]</b> Деактивирован!")

		left.setdefault(chatid, {})
		left[chatid].setdefault("message", "Добро пожаловать в чат!")
		left[chatid].setdefault("is_reply", False)
		self.db.set("left", "left", left)
		await message.edit("<b>[left Mode]</b> Активирован!")
                await asyncio.sleep(5)
                await message.delete()
	async def setleftcmd(self, message):
		"""Установить новое прощание новых пользователей в
		чате.\nИспользуй: .setleft <текст (можно использовать {name}; {
		chat})>; ничего. """
		left = self.db.get("left", "left", {})
		args = utils.get_args_raw(message)
		reply = await message.get_reply_message()
		chatid = str(message.chat_id)
		chat = await message.client.get_entity(int(chatid))
		try:
			if not args and not reply:
				return await message.edit(f'<b>Прощание '
				                          f'пользователей в '
				                          f'"{chat.title}":</b>\n\n'
				                          f'<b>Статус:</b> Включено.\n'
				                          f'<b>прощание:</b> {left[chatid]["message"]}\n\n '
				                          f'<b>~ Установить новое Прощание '
				                          f'можно с помощью команды:</b> '
				                          f'.setleft <текст>.')
			else:
				if reply:
					left[chatid]["message"] = reply.id
					left[chatid]["is_reply"] = True
				else:
					left[chatid]["message"] = args
					left[chatid]["is_reply"] = False
				self.db.set("left", "left", left)
				return await message.edit("<b>Новое прощание установлено "
				                          "успешно!</b>")
		except KeyError:
			return await message.edit(
				f'<b>Прощание пользователей в "{chat.title}":</b>\n\n '
				f'<b>Статус:</b> Отключено')

	async def watcher(self, message):
		"""Интересно, почему он именно watcher называется... 🤔"""
		try:
			left = self.db.get("left", "left", {})
			chatid = str(message.chat_id)
			if chatid not in left: return
			if message.user_left or message.user_deleted:
				user = await message.get_user()
				chat = await message.get_chat()
				if not left[chatid]["is_reply"]:
					return await message.reply(
						(left[chatid]["message"]).format(
							name=user.first_name, chat=chat.title))
				msg = await self.client.get_messages(int(chatid),
				                                     ids=left[chatid][
					                                     "message"])
				await message.reply(msg)
		except:
			pass
