from aiogram.fsm.state import StatesGroup, State


class Towns(StatesGroup):
    town_title = State()


class GuessNumber(StatesGroup):
    number = State()


class CreatePet(StatesGroup):
    name = State()


class SendPublicMessage(StatesGroup):
    message_content = State()
