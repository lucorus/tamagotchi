from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from base import dp, bot
from aiogram.types import Message
from aiogram import types
from emoji import emojize
import base
import games as game


@dp.callback_query(F.data == 'create_pet')
async def pre_create_pet(callback: CallbackQuery):
    game.game_data[callback.from_user.id] = ['create_pet']
    await callback.message.answer('Введите имя для вашего питомца')


async def create_pet(message: Message):
    try:
        name = message.text.split()[0].replace('/', '').capitalize()
        base.create_pet(message.from_user.id, name)
        game.game_data.pop(message.from_user.id)
        await message.answer(f'Питомец с именем {name} создан')
    except:
        await message.answer(f'Вы ввели некорректное имя')


@dp.callback_query(F.data == 'feed')
async def feed_pet(callback: CallbackQuery):
    try:
        pet = base.get_pet_info(callback.from_user.id)
        if pet[1] <= 0:
            await callback.message.answer('У вас недостаточно корма')
        elif pet[7] == pet[9]:
            await callback.message.answer('Питомец сыт')
        else:
            base.feed_pet(callback.from_user.id, pet)
            await callback.message.answer('Питомец накормлен!')
    except Exception as ex:
        await callback.message.answer('Произошла неизвестная ошибка')
        print(ex)


@dp.message(Command('info'))
async def get_pet_info(message: Message):
    pet_info = base.get_pet_info(message.from_user.id)
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

