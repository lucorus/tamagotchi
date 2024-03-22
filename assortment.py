from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from base import dp, bot
from aiogram import types
import base


# на данные момент в магазине есть только корм, но потом добавится ещё что-нибудь
@dp.callback_query(F.data == 'assortment')
async def get_assortment(callback: CallbackQuery):
    await callback.message.delete()
    builder = InlineKeyboardBuilder().add(types.InlineKeyboardButton(
        text="Купить корм за 2 🪙",
        callback_data="buy_food")
    )
    await callback.message.answer(f"Ассортимент:", reply_markup=builder.as_markup())


@dp.callback_query(F.data == 'buy_food')
async def buy_food(callback: CallbackQuery):
    await callback.message.delete()
    try:
        food_price = 2
        if base.get_pet_info(callback.from_user.id)[4] >= food_price:
            base.buy_food(callback.from_user.id, food_price)
            await callback.message.answer('Корм успешно куплен')
        else:
            await callback.message.answer('У вас недостаточно 🪙')
    except Exception as ex:
        await callback.message.answer('Произошла неизвестная ошибка')
        print(ex)
