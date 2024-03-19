from aiogram.types import Message
import sqlite3
import config
import base


async def get_admin_permissions(message: Message, cursor: sqlite3.Cursor):
    if message.text.split()[2] == config.password:
        base.get_admin_status(cursor, message.from_user.id)
        await message.answer('Права администратора получены!')
        await message.delete()
