import asyncio
import logging
import sys
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from emoji import emojize
from base import dp, bot
from aiogram import types, F
import base


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    try:
        if await base.get_user(message.from_user.id) == []:
            await base.create_user(message.from_user.id)
        builder = InlineKeyboardBuilder().add(types.InlineKeyboardButton(
            text="Создать питомца",
            callback_data="create_pet")
        )
        await message.answer(f"Привет, {message.from_user.full_name}!", reply_markup=builder.as_markup())
        await state.clear()
    except Exception as ex:
        print(ex)


@dp.message(Command('users'))
async def users(message: Message):
    users = await base.get_users()
    await message.answer(f'{ [item for item in users] }')


async def send_messages(user_id: list, content_type: str = 'message', *args, **kwargs): #, photo=None, md_text=None, audio=None, voice=None) -> None:
    '''
    Отправляет сообщение с указанными данными в kwargs аргументами всем пользователям из списка id'шников user_id
    '''
    for item in user_id:
        try:
            match content_type:
                case 'text':
                    # 'Ваш питомец погиб:anxious_face_with_sweat:'
                    await bot.send_message(chat_id=int(item), text=emojize(kwargs['md_text']), parse_mode='MARKDOWN')
                    if kwargs['system'] and kwargs['md_text'][0:17] == 'Ваш питомец погиб':
                        # если действие выполняется системой => запрос на отправку сообщений был сделан с целью информирования о смерти
                        await base.delete_pet(int(item))
                case 'photo':
                    await bot.send_photo(chat_id=int(item), photo=kwargs['photo'], caption=emojize(kwargs['md_text']), parse_mode='MARKDOWN')
                case 'document':
                    await bot.send_document(chat_id=int(item), document=kwargs['document'], caption=emojize(kwargs['md_text']), parse_mode='MARKDOWN')
                case 'audio':
                    await bot.send_audio(chat_id=int(item), audio=kwargs['audio'], caption=emojize(kwargs['md_text']), parse_mode='MARKDOWN')
                case 'voice':
                    await bot.send_voice(chat_id=int(item), voice=kwargs['voice'], caption=emojize(kwargs['md_text']), parse_mode='MARKDOWN')
        except Exception as ex:
            print(ex)


# функция, которая раз в 4 часа уменьшает сытость и настроение питомцев
async def change_count_food_and_mood():
    while True:
        await base.change_count_food_and_mood()
        users = await base.check_pet_stats()
        users = [item[0] for item in users]
        await send_messages(user_id=users, content_type='text', md_text='Ваш питомец погиб:anxious_face_with_sweat:', system=True)
        await asyncio.sleep(60 * 60 * 4)


async def main() -> None:
    asyncio.create_task(change_count_food_and_mood())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
