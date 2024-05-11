from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from base import dp, bot
from aiogram.types import Message
from aiogram import types
from emoji import emojize
from base import game_data
import random
import base


# список городов, которые могут попасться/будут считаться верно названными в игре "города"
towns = ['Абакан', 'Абинск', 'Агата', 'Агинское', 'Адлер', 'Адыгейск', 'Азов', 'Алагир', 'Алапаевск', 'Алдан', 'Александров', 'Александрова', 'Александровск', 'Алексин', 'Алупка', 'Алушта', 'Амдерма', 'Амур', 'Амурск', 'Анапа', 'Ангарск', 'Анива', 'Апатиты', 'Апрелевка', 'Апшеронск', 'Аргаяш', 'Ардон', 'Арзамас', 'Армавир', 'Арсеньев', 'Артем', 'Архангесьск', 'Архыз', 'Аршан', 'Асбест', 'Асино', 'Ахтубинск', 'Ачинск', 'Аша', 'Бавлы', 'Байкальск', 'Баксан', 'Балашиха', 'Балашов', 'Балтийск', 'Баргузин', 'Барнаул', 'Баскунчак', 'Батайск', 'Башк', 'Белгород', 'Белогорск', 'Белокуриха', 'Беломорск', 'Белорецк', 'Белореченск', 'Березники', 'Беслан', 'Бийск', 'Билибино', 'Биробиджан', 'Бирск', 'Благовещенск', 'Богучар', 'Бодайбо', 'Бологое', 'Бомнак', 'Бор', 'Борзя', 'Боровск', 'Братск', 'Бреды', 'Бронницы', 'Брянск', 'Бугульма', 'Бугуруслан', 'Буденновск', 'Бузулук', 'Буйнакск', 'Бурят', 'Быково', 'Валаам', 'Ведено', 'Великие', 'Вендинга', 'Верещагино', 'Верхнее', 'Верхотурье', 'Верхоянск', 'Видное', 'Вилюйск', 'Витим', 'Вишера', 'Владивосток', 'Владикавказ', 'Владимир', 'Внуково', 'Воды', 'Волгоград', 'Волгодонск', 'Вологда', 'Волоколамск', 'Волхов', 'Воркута', 'Воронеж', 'Воскресенск', 'Воткинск', 'Всеволожск', 'Вуктыл', 'Выборг', 'Вытегра', 'Вязьма', 'Вятка', 'Гаврилов-Ям', 'Гагарин', 'Галич', 'Гатчина', 'Гдов', 'Геленджик', 'Глазов', 'Голицыно', 'Горно-Алтайск', 'Городовиковск', 'Горы', 'Горячинск', 'Гремячинск', 'Губаха', 'Губкин', 'Гудермес', 'Гурзуф', 'Дагомыс', 'Далматово', 'Данков', 'Дербент', 'Джейрах', 'Джубга', 'Дзержинск', 'Дивногорск', 'Диксон', 'Дмитров', 'Дно', 'Добрянка', 'Долинск', 'Домодедово', 'Дубна', 'Дудинка', 'Егорьевск', 'Ейск', 'Екатеринбург', 'Елабуга', 'Елатьма', 'Елец', 'Ельня', 'Енисейск', 'Ербогачен', 'Ершов', 'Ессентуки', 'ЖелезногорскКурск', 'Жиганск', 'Жигулевск', 'Забайк', 'Забайкальск', 'Заводоуковск', 'Завьялиха', 'Зарайск', 'Звенигород', 'Зеленогорск', 'Зеленоград', 'Златоуст', 'Змеиногорск', 'Иван', 'Иваново', 'Игарка', 'Игирма', 'Игнашино', 'Ижевск', 'Избербаш', 'Инта', 'Ирбит', 'Иркут', 'Иркутск', 'Истра', 'Ишим', 'Йошкар-Ола', 'Кабанск', 'Кажим', 'Калач', 'Калач-на-Дону', 'Калачинск', 'Калевала', 'Калин', 'Калининград', 'Калуга', 'Калязин', 'Камень-на-Оби', 'Камышин', 'Камышлов', 'Кандалакша', 'Каневская', 'Канск', 'Карабудахкент', 'Карабулак', 'Карачаевск', 'Каргасок', 'Карпинск', 'Карталы', 'Касимов', 'Каспийск', 'Катав-Ивановск', 'Катайск', 'Качканар', 'Кашира', 'Кашхатау', 'Кежма', 'Кемерово', 'Кетченеры', 'Кижи', 'Кизел', 'Кизилюрт', 'Кизляр', 'Кимры', 'Кингисепп', 'Кинешма', 'Киренск', 'Киржач', 'Кириши', 'Киров', 'Кирово-Чепецк', 'Кировск', 'Кисловодск', 'Клин', 'Ключ', 'Ковров', 'Когалым', 'Коломна', 'Колпашево', 'Комсомольск-на-Амуре', 'Кондопога', 'Королев', 'Корсаков', 'Костомукша', 'Кострома', 'Котельнич', 'Котлас', 'Кош-Агач', 'Красная', 'Красновишерск', 'Красногорск', 'Краснод', 'Краснодар', 'Краснокамск', 'Красноселькуп', 'Краснотурьинск', 'Красноуральск', 'Красноуфимск', 'Красноярск', 'Кропоткин', 'Крымск', 'Кудымкар', 'Кузнецк', 'Кулу', 'Кулунда', 'Кунгур', 'Курган', 'Курганинск', 'Курильск', 'Курск', 'Куртамыш', 'Курумкан', 'Курчатов', 'Кущевская', 'Кызыл', 'Кырен', 'Кыштым', 'Кяхта', 'Лабинск', 'Лабытнанги', 'Лазаревское', 'Ленин', 'Липецк', 'Листвянка', 'Лодейное', 'Лотошино', 'Луга', 'Луки', 'Луховицы', 'Лысьва', 'Льгов', 'Люберцы', 'Лянтор', 'МГУ', 'Магадан', 'Магас', 'Магнитогорск', 'Майкоп', 'Макаров', 'Макушино', 'Малая', 'Малгобек', 'Малоярославец', 'Мартан', 'Махачкала', 'Медногорск', 'Мелеуз', 'Меренга', 'Миасс', 'Миллерово', 'Минеральные', 'Минусинск', 'Мичуринск', 'Можайск', 'Можга', 'Моздок', 'Мокшан', 'Мончегорск', 'Морд', 'Морозовск', 'Моршанск', 'Моск', 'Москва', 'Муравленко', 'Мураши', 'Мурм', 'Мурманск', 'Муром', 'Мценск', 'Мыс', 'Мытищи', 'Набережные', 'Надым', 'Нальчик', 'Наро-Фоминск', 'Нарткала', 'Нарым', 'Нарьян-Мар', 'Находка', 'Невельск', 'Невинномысск', 'Невьянск', 'Неплюевка', 'Нерчинск', 'Нефедова', 'Нефтегорск', 'Нефтекамск', 'Нефтеюганск', 'Нижневартовск', 'Нижнекамск', 'Нижнеудинск', 'Новая', 'Новгород', 'Новокузнецк', 'Новомичуринск', 'Новомосковск', 'Новороссийка', 'Новороссийск', 'Новосибирск', 'Новочеркасск', 'Ногинск', 'Ноглики', 'Норильск', 'Ноябрьск', 'Нурлат', 'Нязепетровск', 'Обнинск', 'Объячево', 'Одинцово', 'Озеры', 'Оймякон', 'Октябрьское', 'Оленегорск', 'Оленек', 'Омск', 'Онега', 'Орел', 'Оренб', 'Оренбург', 'Орехово-Зуево', 'Орск', 'Оса', 'Оскол', 'Осташков', 'Оха', 'Охотск', 'Павловская', 'Палана', 'Партизанск', 'Певек', 'Пенжино', 'Пенза', 'Перм', 'Петрозаводск', 'Петухово', 'Петушки', 'Печенга', 'Печора', 'Пинега', 'Плес', 'Плесецк', 'Подольск', 'Поле', 'Поляна', 'Поронайск', 'Посад', 'Поярково', 'Приморско-Ахтарск', 'Приозерск', 'Пруды', 'Псков', 'Пушкин', 'Пушкино', 'Пушкинские', 'Пышма', 'Пятигорск', 'Раменское', 'Ребриха', 'Ревда', 'Ржев', 'Рост', 'Ростов', 'Ростов-на-Дону', 'Рубцовск', 'Руза', 'Русса', 'Рыбинск', 'Рыльск', 'Ряжск', 'Салават', 'Салехард', 'Сальск', 'Самар', 'Самара', 'Санкт-Петербург', 'Саранск', 'Сарапул', 'Саратов', 'Саров', 'Сасово', 'Саянск', 'Сверд', 'Светлогорск', 'Северо-Курильск', 'Северобайкальск', 'Северодвинск', 'Североморск', 'Североуральск', 'Сеймчан', 'Семлячики', 'Серафимович', 'Сергиев', 'Серебряные', 'Середниково', 'Серов', 'Серпухов', 'Сибирское', 'Сковородино', 'Славгород', 'Славянск-на-Кубани', 'Сладково', 'Слюдянка', 'Смирных', 'Смоленск', 'Снежинск', 'Снежногорск', 'Соболево', 'Соликамск', 'Солнечногорск', 'Соловки', 'Соль-Илецк', 'Сорочинск', 'Сортавала', 'Сосногорск', 'Сосьва', 'Сочи', 'Старая', 'Стерлитамак', 'Ступино', 'Судак', 'Сузун', 'Сунтар', 'Сургут', 'Сусуман', 'Сухиничи', 'Сыктывкар', 'Тавда', 'Таганрог', 'Тагил', 'Тайшет', 'Талдом', 'Тамбов', 'Тарко-Сале', 'Таштагол', 'Теберда', 'Темрюк', 'Териберка', 'Терскол', 'Тикси', 'Тимашевск', 'Тихвин', 'Тихорецк', 'Тобольск', 'Токма', 'Токсово', 'Тольятти', 'Томари', 'Томпа', 'Томск', 'Торжок', 'Тосно', 'Тотьма', 'Троицк', 'Троицко-Печорск', 'Туапсе', 'Тула', 'Тулпан', 'Тулун', 'Тура', 'Туруханск', 'Тутаев', 'Тутончаны', 'Тымовское', 'Тында', 'Тырныауз', 'Уварово', 'Углегорск', 'Углич', 'Улан-Удэ', 'Ульяновск', 'Урус-Мартан', 'Урюпинск', 'Усинск', 'Усолье', 'Уссурийск', 'Усть-Баргузин', 'Усть-Джегута', 'Усть-Илимск', 'Усть-Ишим', 'Усть-Калманка', 'Усть-Камчатск', 'Усть-Катав', 'Усть-Кулом', 'Усть-Кут', 'Устюг', 'Устюжна', 'Уфа', 'Ухта', 'Учалы', 'Уэлен', 'Фатеж', 'Феодосия', 'Хабаровск', 'Хант', 'Ханты-Мансийск', 'Хасавюрт', 'Хасан', 'Хатанга', 'Химки', 'Холмогоры', 'Холмск', 'Хоста', 'Хужир', 'Цимлянск', 'Чебоксары', 'Чегем', 'Челны', 'Челюскин', 'Челяб', 'Челябинск', 'Черемхово', 'Череповец', 'Черкесск', 'Чермоз', 'Черняховск', 'Черусти', 'Чехов', 'Чикола', 'Чита', 'Чокурдах', 'Чулым', 'Шадринск', 'Шали', 'Шамары', 'Шарья', 'Шатки', 'Шатура', 'Шаховская', 'Шахты', 'Шелагонцы', 'Шелехов', 'Шенкурск', 'Шерегеш', 'Шереметьево', 'Шилка', 'Шмидта', 'Шумиха', 'Шуя', 'Щелково', 'Щельяюр', 'Элиста', 'Эльбрус', 'Эльтон', 'Энгельс', 'Югорск', 'Южно-Курильск', 'Южно-Сахалинск', 'Южноуральск', 'Юровск', 'Юрьевец', 'Якут', 'Якутск', 'Якша', 'Ялта', 'Ялуторовск', 'Ямбург', 'Яр-Сале', 'Яхрома', 'Яшалта']


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
    game_data[callback.from_user.id] = ['guess_number', random.randint(1, 100)]
    await callback.message.answer(f"Я загадал число от 1 до 100, попробуй угадать его.")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


@dp.callback_query(F.data == "towns")
async def start_game_towns(callback: CallbackQuery):
    game_data[callback.from_user.id] = ['towns', random.choice(towns)]
    await callback.message.answer(f"Я загадал город, его название - { game_data[callback.from_user.id][1] }."
                         f"\n Ваша задача - назвать российский город на последнюю букву")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


# обработка ответов для игры угадай число
async def guess_number(message: Message):
    guessed_number = game_data[message.from_user.id][1]

    try:
        user_number = int(message.text)
    except ValueError:
        await message.answer("Введите число -_-")
        return

    if user_number == guessed_number:
        await message.answer(emojize("Поздравляю! Ты угадал число"))
        await base.add_coins(message.from_user.id, 2)
        await base.add_mood(message.from_user.id, 5)
        game_data.pop(message.from_user.id)
    elif user_number < guessed_number:
        await message.answer(emojize("Загаданное число больше :up_arrow:"))
    else:
        await message.answer(emojize("Загаданное число меньше :down_arrow:"))


# обработка ответов для игры в города
async def game_towns(message: types.Message):
    try:
        if game_data[message.from_user.id][1][-1] == message.text[0].lower() and message.text.capitalize() in towns \
                and message.text != game_data[message.from_user.id]:
            await message.answer('Правильный ответ')
            await base.add_coins(message.from_user.id, 2)
            await base.add_mood(message.from_user.id, 5)
        else:
            await message.answer(
                emojize('Неправильный ответ, вы проиграли :index_pointing_at_the_viewer::face_with_tears_of_joy:')
            )
    except Exception as ex:
        print(ex)
    finally:
        game_data.pop(message.from_user.id)
