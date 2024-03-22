import asyncio
import logging
import sys
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from emoji import emojize
from base import dp, bot, cursor
from aiogram import types, F
import games as game
import admin, base, pet, assortment


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES(?)', (message.from_user.id,))
    cursor.connection.commit()
    builder = InlineKeyboardBuilder().add(types.InlineKeyboardButton(
        text="Создать питомца",
        callback_data="create_pet")
    )
    await message.answer(f"Привет, { message.from_user.full_name }!", reply_markup=builder.as_markup())


async def send_message(user_id: list) -> None:
    for item in user_id:
        await bot.send_message(chat_id=item[0], text=emojize('Ваш питомец погиб:anxious_face_with_sweat:'))
        base.delete_pet(item[0])


# функция, которая раз в 4 часа уменьшает сытость и настроение питомцев
async def change_count_food_and_mood():
    while True:
        base.change_count_food_and_mood()
        users = base.check_pet_stats()
        await send_message(users)
        await asyncio.sleep(60 * 60 * 4)


@dp.message()
async def messages(message: types.Message):
    try:
        match game.game_data[message.from_user.id][0]:
            case 'guess_number':
                await game.guess_number(message)
            case 'create_pet':
                await pet.create_pet(message)
            case 'towns':
                await game.game_towns(message)
            case 'send_message':
                await admin.send_public_message(message)
    except:
        # пользователь не играет ни в какую игру
        pass


async def main() -> None:
    asyncio.create_task(change_count_food_and_mood())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
