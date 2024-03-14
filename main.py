import asyncio
import logging
import sqlite3
import sys
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import base
import config
from aiogram import Bot, Dispatcher, types, F
import random


dp = Dispatcher()
# Словарь в котором хранятся данные о всех активных играх
# {user_id: ['название_игры', 'данные, которые нужны для данной игры'], }
game_data = dict()
# список городов, которые могут попасться/будут считаться верно названными в игре "города"
towns = ['Абакан', 'Абинск', 'Агата', 'Агинское', 'Адлер', 'Адыгейск', 'Азов', 'Алагир', 'Алапаевск', 'Алдан', 'Александров', 'Александрова', 'Александровск', 'Алексин', 'Алупка', 'Алушта', 'Амдерма', 'Амур', 'Амурск', 'Анапа', 'Ангарск', 'Анива', 'Апатиты', 'Апрелевка', 'Апшеронск', 'Аргаяш', 'Ардон', 'Арзамас', 'Армавир', 'Арсеньев', 'Артем', 'Архангесьск', 'Архыз', 'Аршан', 'Асбест', 'Асино', 'Ахтубинск', 'Ачинск', 'Аша', 'Бавлы', 'Байкальск', 'Баксан', 'Балашиха', 'Балашов', 'Балтийск', 'Баргузин', 'Барнаул', 'Баскунчак', 'Батайск', 'Башк', 'Белгород', 'Белогорск', 'Белокуриха', 'Беломорск', 'Белорецк', 'Белореченск', 'Березники', 'Беслан', 'Бийск', 'Билибино', 'Биробиджан', 'Бирск', 'Благовещенск', 'Богучар', 'Бодайбо', 'Бологое', 'Бомнак', 'Бор', 'Борзя', 'Боровск', 'Братск', 'Бреды', 'Бронницы', 'Брянск', 'Бугульма', 'Бугуруслан', 'Буденновск', 'Бузулук', 'Буйнакск', 'Бурят', 'Быково', 'Валаам', 'Ведено', 'Великие', 'Вендинга', 'Верещагино', 'Верхнее', 'Верхотурье', 'Верхоянск', 'Видное', 'Вилюйск', 'Витим', 'Вишера', 'Владивосток', 'Владикавказ', 'Владимир', 'Внуково', 'Воды', 'Волгоград', 'Волгодонск', 'Вологда', 'Волоколамск', 'Волхов', 'Воркута', 'Воронеж', 'Воскресенск', 'Воткинск', 'Всеволожск', 'Вуктыл', 'Выборг', 'Вытегра', 'Вязьма', 'Вятка', 'Гаврилов-Ям', 'Гагарин', 'Галич', 'Гатчина', 'Гдов', 'Геленджик', 'Глазов', 'Голицыно', 'Горно-Алтайск', 'Городовиковск', 'Горы', 'Горячинск', 'Гремячинск', 'Губаха', 'Губкин', 'Гудермес', 'Гурзуф', 'Дагомыс', 'Далматово', 'Данков', 'Дербент', 'Джейрах', 'Джубга', 'Дзержинск', 'Дивногорск', 'Диксон', 'Дмитров', 'Дно', 'Добрянка', 'Долинск', 'Домодедово', 'Дубна', 'Дудинка', 'Егорьевск', 'Ейск', 'Екатеринбург', 'Елабуга', 'Елатьма', 'Елец', 'Ельня', 'Енисейск', 'Ербогачен', 'Ершов', 'Ессентуки', 'ЖелезногорскКурск', 'Жиганск', 'Жигулевск', 'Забайк', 'Забайкальск', 'Заводоуковск', 'Завьялиха', 'Зарайск', 'Звенигород', 'Зеленогорск', 'Зеленоград', 'Златоуст', 'Змеиногорск', 'Иван', 'Иваново', 'Игарка', 'Игирма', 'Игнашино', 'Ижевск', 'Избербаш', 'Инта', 'Ирбит', 'Иркут', 'Иркутск', 'Истра', 'Ишим', 'Йошкар-Ола', 'Кабанск', 'Кажим', 'Калач', 'Калач-на-Дону', 'Калачинск', 'Калевала', 'Калин', 'Калининград', 'Калуга', 'Калязин', 'Камень-на-Оби', 'Камышин', 'Камышлов', 'Кандалакша', 'Каневская', 'Канск', 'Карабудахкент', 'Карабулак', 'Карачаевск', 'Каргасок', 'Карпинск', 'Карталы', 'Касимов', 'Каспийск', 'Катав-Ивановск', 'Катайск', 'Качканар', 'Кашира', 'Кашхатау', 'Кежма', 'Кемерово', 'Кетченеры', 'Кижи', 'Кизел', 'Кизилюрт', 'Кизляр', 'Кимры', 'Кингисепп', 'Кинешма', 'Киренск', 'Киржач', 'Кириши', 'Киров', 'Кирово-Чепецк', 'Кировск', 'Кисловодск', 'Клин', 'Ключ', 'Ковров', 'Когалым', 'Коломна', 'Колпашево', 'Комсомольск-на-Амуре', 'Кондопога', 'Королев', 'Корсаков', 'Костомукша', 'Кострома', 'Котельнич', 'Котлас', 'Кош-Агач', 'Красная', 'Красновишерск', 'Красногорск', 'Краснод', 'Краснодар', 'Краснокамск', 'Красноселькуп', 'Краснотурьинск', 'Красноуральск', 'Красноуфимск', 'Красноярск', 'Кропоткин', 'Крымск', 'Кудымкар', 'Кузнецк', 'Кулу', 'Кулунда', 'Кунгур', 'Курган', 'Курганинск', 'Курильск', 'Курск', 'Куртамыш', 'Курумкан', 'Курчатов', 'Кущевская', 'Кызыл', 'Кырен', 'Кыштым', 'Кяхта', 'Лабинск', 'Лабытнанги', 'Лазаревское', 'Ленин', 'Липецк', 'Листвянка', 'Лодейное', 'Лотошино', 'Луга', 'Луки', 'Луховицы', 'Лысьва', 'Льгов', 'Люберцы', 'Лянтор', 'МГУ', 'Магадан', 'Магас', 'Магнитогорск', 'Майкоп', 'Макаров', 'Макушино', 'Малая', 'Малгобек', 'Малоярославец', 'Мартан', 'Махачкала', 'Медногорск', 'Мелеуз', 'Меренга', 'Миасс', 'Миллерово', 'Минеральные', 'Минусинск', 'Мичуринск', 'Можайск', 'Можга', 'Моздок', 'Мокшан', 'Мончегорск', 'Морд', 'Морозовск', 'Моршанск', 'Моск', 'Москва', 'Муравленко', 'Мураши', 'Мурм', 'Мурманск', 'Муром', 'Мценск', 'Мыс', 'Мытищи', 'Набережные', 'Надым', 'Нальчик', 'Наро-Фоминск', 'Нарткала', 'Нарым', 'Нарьян-Мар', 'Находка', 'Невельск', 'Невинномысск', 'Невьянск', 'Неплюевка', 'Нерчинск', 'Нефедова', 'Нефтегорск', 'Нефтекамск', 'Нефтеюганск', 'Нижневартовск', 'Нижнекамск', 'Нижнеудинск', 'Новая', 'Новгород', 'Новокузнецк', 'Новомичуринск', 'Новомосковск', 'Новороссийка', 'Новороссийск', 'Новосибирск', 'Новочеркасск', 'Ногинск', 'Ноглики', 'Норильск', 'Ноябрьск', 'Нурлат', 'Нязепетровск', 'Обнинск', 'Объячево', 'Одинцово', 'Озеры', 'Оймякон', 'Октябрьское', 'Оленегорск', 'Оленек', 'Омск', 'Онега', 'Орел', 'Оренб', 'Оренбург', 'Орехово-Зуево', 'Орск', 'Оса', 'Оскол', 'Осташков', 'Оха', 'Охотск', 'Павловская', 'Палана', 'Партизанск', 'Певек', 'Пенжино', 'Пенза', 'Перм', 'Петрозаводск', 'Петухово', 'Петушки', 'Печенга', 'Печора', 'Пинега', 'Плес', 'Плесецк', 'Подольск', 'Поле', 'Поляна', 'Поронайск', 'Посад', 'Поярково', 'Приморско-Ахтарск', 'Приозерск', 'Пруды', 'Псков', 'Пушкин', 'Пушкино', 'Пушкинские', 'Пышма', 'Пятигорск', 'Раменское', 'Ребриха', 'Ревда', 'Ржев', 'Рост', 'Ростов', 'Ростов-на-Дону', 'Рубцовск', 'Руза', 'Русса', 'Рыбинск', 'Рыльск', 'Ряжск', 'Салават', 'Салехард', 'Сальск', 'Самар', 'Самара', 'Санкт-Петербург', 'Саранск', 'Сарапул', 'Саратов', 'Саров', 'Сасово', 'Саянск', 'Сверд', 'Светлогорск', 'Северо-Курильск', 'Северобайкальск', 'Северодвинск', 'Североморск', 'Североуральск', 'Сеймчан', 'Семлячики', 'Серафимович', 'Сергиев', 'Серебряные', 'Середниково', 'Серов', 'Серпухов', 'Сибирское', 'Сковородино', 'Славгород', 'Славянск-на-Кубани', 'Сладково', 'Слюдянка', 'Смирных', 'Смоленск', 'Снежинск', 'Снежногорск', 'Соболево', 'Соликамск', 'Солнечногорск', 'Соловки', 'Соль-Илецк', 'Сорочинск', 'Сортавала', 'Сосногорск', 'Сосьва', 'Сочи', 'Старая', 'Стерлитамак', 'Ступино', 'Судак', 'Сузун', 'Сунтар', 'Сургут', 'Сусуман', 'Сухиничи', 'Сыктывкар', 'Тавда', 'Таганрог', 'Тагил', 'Тайшет', 'Талдом', 'Тамбов', 'Тарко-Сале', 'Таштагол', 'Теберда', 'Темрюк', 'Териберка', 'Терскол', 'Тикси', 'Тимашевск', 'Тихвин', 'Тихорецк', 'Тобольск', 'Токма', 'Токсово', 'Тольятти', 'Томари', 'Томпа', 'Томск', 'Торжок', 'Тосно', 'Тотьма', 'Троицк', 'Троицко-Печорск', 'Туапсе', 'Тула', 'Тулпан', 'Тулун', 'Тура', 'Туруханск', 'Тутаев', 'Тутончаны', 'Тымовское', 'Тында', 'Тырныауз', 'Уварово', 'Углегорск', 'Углич', 'Улан-Удэ', 'Ульяновск', 'Урус-Мартан', 'Урюпинск', 'Усинск', 'Усолье', 'Уссурийск', 'Усть-Баргузин', 'Усть-Джегута', 'Усть-Илимск', 'Усть-Ишим', 'Усть-Калманка', 'Усть-Камчатск', 'Усть-Катав', 'Усть-Кулом', 'Усть-Кут', 'Устюг', 'Устюжна', 'Уфа', 'Ухта', 'Учалы', 'Уэлен', 'Фатеж', 'Феодосия', 'Хабаровск', 'Хант', 'Ханты-Мансийск', 'Хасавюрт', 'Хасан', 'Хатанга', 'Химки', 'Холмогоры', 'Холмск', 'Хоста', 'Хужир', 'Цимлянск', 'Чебоксары', 'Чегем', 'Челны', 'Челюскин', 'Челяб', 'Челябинск', 'Черемхово', 'Череповец', 'Черкесск', 'Чермоз', 'Черняховск', 'Черусти', 'Чехов', 'Чикола', 'Чита', 'Чокурдах', 'Чулым', 'Шадринск', 'Шали', 'Шамары', 'Шарья', 'Шатки', 'Шатура', 'Шаховская', 'Шахты', 'Шелагонцы', 'Шелехов', 'Шенкурск', 'Шерегеш', 'Шереметьево', 'Шилка', 'Шмидта', 'Шумиха', 'Шуя', 'Щелково', 'Щельяюр', 'Элиста', 'Эльбрус', 'Эльтон', 'Энгельс', 'Югорск', 'Южно-Курильск', 'Южно-Сахалинск', 'Южноуральск', 'Юровск', 'Юрьевец', 'Якут', 'Якутск', 'Якша', 'Ялта', 'Ялуторовск', 'Ямбург', 'Яр-Сале', 'Яхрома', 'Яшалта']


@dp.message(Command('games'))
async def games(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Угадай число",
        callback_data="guess_number")
    )
    builder.add(types.InlineKeyboardButton(
        text="Города",
        callback_data="towns")
    )
    await message.answer(
        "В какую игру хочешь сыграть?",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "guess_number")
async def start_game_guess_number(callback: CallbackQuery):
    game_data[callback.from_user.id] = ['guess_number', random.randint(1, 100)]
    await callback.message.answer(f"Я загадал число от 1 до 100, попробуй угадать его.")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


@dp.callback_query(F.data == "towns")
async def start_game_towns(callback: CallbackQuery):
    game_data[callback.from_user.id] = ['towns', random.choice(towns)]
    await callback.message.answer(f"Я загадал город, его название - { game_data[callback.from_user.id][1] }."
                         f"Ваша задача назвать город на последнюю букву")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


@dp.callback_query(F.data == 'create_pet')
async def pre_create_pet(callback: CallbackQuery):
    game_data[callback.from_user.id] = ['create_pet']
    await callback.message.answer('Введите имя для вашего питомца')


async def create_pet(message: Message):
    try:
        name = message.text.split()[0].capitalize()
        base.create_pet(cursor, message.from_user.id, name)
        game_data.pop(message.from_user.id)
        await message.answer(f'Питомец с именем {name} создан')
    except:
        await message.answer(f'Вы ввели некорректное имя')


@dp.message(Command('feed'))
async def feed_pet(message: Message):
    try:
        base.feed_pet(cursor, message.from_user.id)
        await message.answer('Питомец накормлен!')
    except Exception as ex:
        await message.answer('Произошла неизвестная ошибка')
        print(ex)


# на данные момент в магазине есть только корм, но потом добавится ещё что-нибудь
@dp.message(Command('assortment'))
async def get_assortment(message: Message):
    builder = InlineKeyboardBuilder().add(types.InlineKeyboardButton(
        text="Купить корм за 1 🪙",
        callback_data="buy_food")
    )
    await message.answer(f"Ассортимент:", reply_markup=builder.as_markup())


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


async def main() -> None:
    global connection, cursor, bot
    connection = sqlite3.connect('files.db', check_same_thread=True)
    cursor = connection.cursor()
    bot = Bot(config.token)
    asyncio.create_task(change_count_food_and_mood())
    await dp.start_polling(bot)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES(?)', (message.from_user.id,))
    cursor.connection.commit()
    builder = InlineKeyboardBuilder().add(types.InlineKeyboardButton(
        text="Создать питомца",
        callback_data="create_pet")
    )
    await message.answer(f"Привет, { message.from_user.full_name }!", reply_markup=builder.as_markup())


@dp.message(Command('pet_info'))
async def get_pet_info(message: Message):
    await message.answer(f'Информация о вашем питомце: \n'
                         f' { base.get_pet_info(cursor, message.from_user.id) }')


@dp.message(Command('get_admin_status'))
async def get_admin_status(message: Message):
    if message.text.replace('/get_admin_status ', '') == config.password:
        base.get_admin_status(cursor, message.from_user.id)
        await message.answer('Права администратора получены!')
        await message.delete()


# функция, которая раз в 4 часа уменьшает сытость и настроение питомцев
async def change_count_food_and_mood():
    while True:
        base.change_count_food_and_mood(cursor)
        await asyncio.sleep(60 * 60 * 4)


# обработка ответов для игры угадай число
async def guess_number(message: Message):
    guessed_number = game_data[message.from_user.id][1]

    try:
        user_number = int(message.text)
    except ValueError:
        await message.answer("Введите число.")
        return

    if user_number == guessed_number:
        await message.answer("Поздравляю! Ты угадал число.")
        base.add_coins(cursor, message.from_user.id, 2)
        base.add_mood(cursor, message.from_user.id, 5)
        game_data.pop(message.from_user.id)
    elif user_number < guessed_number:
        await message.answer("Загаданное число больше.")
    else:
        await message.answer("Загаданное число меньше.")


# обработка ответов для игры в города
async def game_towns(message: types.Message):
    try:
        if game_data[message.from_user.id][1][-1] == message.text[0].lower() and message.text.capitalize() in towns \
                and message.text != game_data[message.from_user.id]:
            await message.answer('Вы молодцы!')
            base.add_coins(cursor, message.from_user.id, 2)
            base.add_mood(cursor, message.from_user.id, 5)
        else:
            await message.answer('Неправильный ответ, вы проиграли')
    except Exception as ex:
        print(ex)
    finally:
        game_data.pop(message.from_user.id)


# распределение сообщений без команды на игры
@dp.message()
async def messages(message: types.Message):
    try:
        if game_data[message.from_user.id][0] == 'guess_number':
            await guess_number(message)
        elif game_data[message.from_user.id][0] == 'create_pet':
            await create_pet(message)
        elif game_data[message.from_user.id][0] == 'towns':
            await game_towns(message)
    except:
        # пользователь не играет ни в какую игру
        pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
