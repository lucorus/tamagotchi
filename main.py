import asyncio
import logging
import sqlite3
import sys

import emoji
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from emoji import emojize

import admin
import base
import config
from aiogram import Bot, Dispatcher, types, F
import random
import games as game

dp = Dispatcher()
global connection, cursor, bot
connection = sqlite3.connect('files.db', check_same_thread=True)
cursor = connection.cursor()
bot = Bot(config.token)


@dp.callback_query(F.data == 'games')
async def get_games(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text=emojize("Угадай число :slot_machine:"),
        callback_data="guess_number")
    )
    builder.add(types.InlineKeyboardButton(
        text=emojize("Города :cityscape:"),
        callback_data="towns")
    )
    await callback.message.answer(
        "В какую игру хочешь сыграть?",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "guess_number")
async def start_game_guess_number(callback: CallbackQuery):
    game.game_data[callback.from_user.id] = ['guess_number', random.randint(1, 100)]
    await callback.message.answer(f"Я загадал число от 1 до 100, попробуй угадать его.")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


@dp.callback_query(F.data == "towns")
async def start_game_towns(callback: CallbackQuery):
    game.game_data[callback.from_user.id] = ['towns', random.choice(game.towns)]
    await callback.message.answer(f"Я загадал город, его название - { game.game_data[callback.from_user.id][1] }."
                         f"\n Ваша задача - назвать российский город на последнюю букву")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


@dp.callback_query(F.data == 'create_pet')
async def pre_create_pet(callback: CallbackQuery):
    game.game_data[callback.from_user.id] = ['create_pet']
    await callback.message.answer('Введите имя для вашего питомца')


async def create_pet(message: Message):
    try:
        name = message.text.split()[0].replace('/', '').capitalize()
        base.create_pet(cursor, message.from_user.id, name)
        game.game_data.pop(message.from_user.id)
        await message.answer(f'Питомец с именем {name} создан')
    except:
        await message.answer(f'Вы ввели некорректное имя')


@dp.callback_query(F.data == 'feed')
async def feed_pet(callback: CallbackQuery):
    try:
        base.feed_pet(cursor, callback.from_user.id)
        await callback.message.answer('Питомец накормлен!')
    except Exception as ex:
        await callback.message.answer('Произошла неизвестная ошибка')
        print(ex)


# на данные момент в магазине есть только корм, но потом добавится ещё что-нибудь
@dp.callback_query(F.data == 'assortment')
async def get_assortment(callback: CallbackQuery):
    builder = InlineKeyboardBuilder().add(types.InlineKeyboardButton(
        text="Купить корм за 1 🪙",
        callback_data="buy_food")
    )
    await callback.message.answer(f"Ассортимент:", reply_markup=builder.as_markup())


@dp.callback_query(F.data == 'buy_food')
async def buy_food(callback: CallbackQuery):
    try:
        if base.get_pet_info(cursor, callback.from_user.id)[4] >= 1:
            base.buy_food(cursor, callback.from_user.id)
            await callback.message.answer('Корм успешно куплен')
        else:
            await callback.message.answer('У вас недостаточно 🪙')
    except Exception as ex:
        await callback.message.answer('Произошла неизвестная ошибка')
        print(ex)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES(?)', (message.from_user.id,))
    cursor.connection.commit()
    builder = InlineKeyboardBuilder().add(types.InlineKeyboardButton(
        text="Создать питомца",
        callback_data="create_pet")
    )
    await message.answer(f"Привет, { message.from_user.full_name }!", reply_markup=builder.as_markup())


@dp.message(Command('info'))
async def get_pet_info(message: Message):
    pet_info = base.get_pet_info(cursor, message.from_user.id)
    builder = InlineKeyboardBuilder()
    if pet_info[2] == None:
        # если питомца ещё нет, то предлагаем его создать
        builder.add(types.InlineKeyboardButton(
            text="Создать питомца",
            callback_data="create_pet")
        )
        await message.answer('У вас ещё нет питомца', reply_markup=builder.as_markup())
    else:
        builder.row(types.InlineKeyboardButton(
            text=emojize("Игры :video_game:"),
            callback_data="games")
        )

        builder.row(types.InlineKeyboardButton(
            text=emojize("Магазин :money_with_wings:"),
            callback_data="assortment")
        )

        builder.row(types.InlineKeyboardButton(
            text=emojize("Покормить :paw_prints:"),
            callback_data="feed")
        )
        await message.answer(
            f'''
            { pet_info[6] } \n Еда: {pet_info[7]} / {pet_info[9]} \n Настроение: {pet_info[8]} / { pet_info[10]} \n Количество корма: { pet_info[1] } \n Монет: { pet_info[4] }🪙
            ''',
            reply_markup=builder.as_markup()
        )


# пользователь/админ вводит команду /admin_panel *команда администратора, которую он хочет использовать*
@dp.message(Command('admin_panel'))
async def admin_panel(message: Message):
    # получаем название команды администратора
    match message.text.split()[1]:
        case 'send_message':
            pass
        case 'get_admin_permissions':
            await admin.get_admin_permissions(message, cursor)


# рассылает сообщения пользователям с информацией о смерти их питомца :(
async def send_message(user_id: list) -> None:
    for item in user_id:
        await bot.send_message(chat_id=item[0], text=emojize('Ваш питомец погиб:anxious_face_with_sweat:'))
        base.delete_pet(cursor, item[0])


# функция, которая раз в 4 часа уменьшает сытость и настроение питомцев
async def change_count_food_and_mood():
    while True:
        base.change_count_food_and_mood(cursor)
        users = base.check_pet_stats(cursor)
        await send_message(users)
        await asyncio.sleep(60 * 60 * 4)


@dp.message()
async def messages(message: types.Message):
    try:
        if game.game_data[message.from_user.id][0] == 'guess_number':
            await game.guess_number(message)
        elif game.game_data[message.from_user.id][0] == 'create_pet':
            await create_pet(message)
        elif game.game_data[message.from_user.id][0] == 'towns':
            await game.game_towns(message)
    except:
        # пользователь не играет ни в какую игру
        pass


async def main() -> None:
    asyncio.create_task(change_count_food_and_mood())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
