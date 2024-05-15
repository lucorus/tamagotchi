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
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
            text="Купить корм за 2 🪙",
            callback_data="buy_food"
        ))
    builder.row(types.InlineKeyboardButton(
            text="Увеличить максимальный показатель еды на 1 за 100🪙",
            callback_data="upgrade_max_food"
        ))
    builder.row(types.InlineKeyboardButton(
            text="Увеличить максимальный показатель настроения на 10 за 100🪙",
            callback_data="upgrade_max_mood"
        ))
    await callback.message.answer(f"Ассортимент:", reply_markup=builder.as_markup())


# проверяем может ли пользователь купить товар
async def can_buy_item(user_id: int, price: int) -> bool:
    try:
        pet_info = await base.get_pet_info(user_id)
        if pet_info[4] >= price:
            return True
        return False
    except Exception as ex:
        print(ex)
        return False


@dp.callback_query(F.data == 'buy_food')
async def buy_food(callback: CallbackQuery):
    await callback.message.delete()
    try:
        food_price = 2
        if await can_buy_item(callback.from_user.id, food_price):
            await base.buy_food(callback.from_user.id, food_price)
            await callback.message.answer('Корм успешно куплен')
        else:
            await callback.message.answer('У вас недостаточно 🪙')
    except Exception as ex:
        await callback.message.answer('Произошла неизвестная ошибка')
        print(ex)


@dp.callback_query(F.data == 'upgrade_max_food')
async def upgrade_max_food(callback: CallbackQuery):
    await callback.message.delete()
    try:
        if await can_buy_item(callback.from_user.id, 0):
            await base.upgrade_stats(callback.from_user.id, 0, 'food')
            await callback.message.answer('Максимальный показатель еды увеличен!')
        else:
            await callback.message.answer('У вас недостаточно 🪙')
    except Exception as ex:
        await callback.message.answer('Произошла неизвестная ошибка')
        print(ex)


@dp.callback_query(F.data == 'upgrade_max_mood')
async def upgrade_max_mood(callback: CallbackQuery):
    await callback.message.delete()
    try:
        if await can_buy_item(callback.from_user.id, 0):
            await base.upgrade_stats(callback.from_user.id, 0, 'mood')
            await callback.message.answer('Максимальный показатель настроения увеличен!')
        else:
            await callback.message.answer('У вас недостаточно 🪙')
    except Exception as ex:
        await callback.message.answer('Произошла неизвестная ошибка')
        print(ex)

