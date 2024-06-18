from aiogram import types, F
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from emoji import emojize
import config
import base
import main
import states
from base import dp


@dp.message(Command('admin_panel'))
async def admin_panel(message: Message):
    builder = InlineKeyboardBuilder()
    if await base.is_admin(message.from_user.id):
        builder.row(types.InlineKeyboardButton(
            text=emojize("Отправить сообщение:pencil:"),
            callback_data="send_public_message")
        )
        builder.row(types.InlineKeyboardButton(
            text=emojize("Список администраторов:bookmark_tabs:"),
            callback_data="admin_list")
        )
        await message.answer('Возможные действия', reply_markup=builder.as_markup())


@dp.message(Command('get_admin_permissions'))
async def get_admin_permissions(message: Message):
    try:
        if message.text.split()[1] == config.password:
            await base.give_admin_permissions(message.from_user.id)
            await message.answer('Права администратора получены!')
            await message.delete()
    except Exception as ex:
        print(ex)


@dp.callback_query(F.data == 'admin_list')
async def admin_list(callback: CallbackQuery):
    await callback.message.delete()
    admins = await base.get_admins()
    adm_list = ['Администраторы:']
    for item in admins:
        user = dict(await base.bot.get_chat(item[0]))
        adm_list += \
            f'''
            
            ID: {item[0]}
            Username: {user['first_name'] + '' if user['last_name'] == None else user['last_name']}
            link: @{user['username']}
            '''
    await callback.message.answer(''.join(adm_list))


@dp.message(Command('delete_admin'))
async def delete_admin(message: Message):
    try:
        if await base.is_admin(message.from_user.id):
            await base.delete_admin(int(message.text.split()[1]))
            await message.answer(emojize(f'Администратор с id = { message.text.split()[1] } был разжалован:anxious_face_with_sweat:'))
            await base.bot.send_message(chat_id=message.text.split()[1],
                                        text=emojize('Вы были разжалованы с роли администратора:pensive_face:')
                                        )
    except ValueError:
        await message.answer(emojize('Вы ввели неправильный тип данных:face_with_symbols_on_mouth:'))
    except Exception as ex:
        print(ex)
        await message.answer('Произошла неизвестная ошибка')


@dp.callback_query(F.data == 'send_public_message')
async def pre_send_public_message(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
        await state.set_state(states.SendPublicMessage.message_content)
        await callback.message.answer('Введите текст сообщения, которое вы хотите отправить')
    except Exception as ex:
        print(ex)
        await callback.message.answer('Произошла неизвестная ошибка')


# отправляет сообщение всем пользователям с текстом, написанным админом
@dp.message(states.SendPublicMessage.message_content)
async def send_public_message(message: Message, state: FSMContext):
    try:
        await state.clear()
        if message.media_group_id != None:
            await message.answer('Групповые медиа не поддерживаются')
            return
        user_id = await base.get_users_id()
        match message.content_type:
            case ContentType.PHOTO:
                await main.send_messages(user_id=user_id, content_type='photo', md_text=message.md_text, photo=message.photo[0].file_id)
            case ContentType.DOCUMENT:
                await main.send_messages(user_id=user_id, content_type='document', md_text=message.md_text, document=message.document.file_id)
            case ContentType.AUDIO:
                await main.send_messages(user_id=user_id, content_type='audio', md_text=message.md_text, audio=message.audio.file_id)
            case ContentType.VOICE:
                await main.send_messages(user_id=user_id, content_type='voice', md_text=message.md_text, voice=message.voice.file_id)
            case ContentType.TEXT:
                await main.send_messages(user_id=user_id, content_type='text', md_text=message.md_text)
    except Exception as ex:
        print(ex)

