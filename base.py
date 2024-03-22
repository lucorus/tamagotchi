import uuid
import sqlite3
import config
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

# Словарь, который хранит данные о всех активных действиях пользователей
# {user_id: ['название_действия', данные, которые нужны для данного действия/ничего], }
game_data = dict()
dp = Dispatcher()
global cursor, bot
connection = sqlite3.connect('files.db', check_same_thread=True)
cursor = connection.cursor()
# session = AiohttpSession(proxy=config.PROXY_URL)
# bot = Bot(token=config.token, session=session)
bot = Bot(config.token)


def feed_pet(user_id: int, pet: list) -> None:
    cursor.execute(
        '''
        UPDATE users SET food = food - 1 WHERE id=?
        ''', (user_id, )
    )
    cursor.execute(
        '''
        UPDATE pet SET food = food + 1 WHERE uuid=?
        ''', (pet[5], )
    )
    cursor.connection.commit()


def add_coins(user_id: int, coins: int = 1) -> None:
    cursor.execute('UPDATE users SET coins=coins+? WHERE id=?;', (coins, user_id))
    cursor.connection.commit()


def add_mood(user_id: int, mood: int = 5) -> None:
    pet = get_pet_info(user_id)
    cursor.execute('UPDATE pet SET mood=mood+? WHERE uuid=?;', (mood, pet[2]))
    cursor.execute('UPDATE pet SET mood=max_mood WHERE uuid=? AND mood>?', (pet[2], pet[10]))
    cursor.connection.commit()


def buy_food(user_id: int, food_price: int):
    cursor.execute('UPDATE users SET food = food + 1, coins = coins - ? WHERE id=?', (food_price, user_id))
    cursor.connection.commit()


def create_pet(user_id: int, name: str) -> None:
    pet_uuid = str(uuid.uuid4())
    cursor.execute('INSERT INTO pet (uuid, name) VALUES(?, ?);', (pet_uuid, name))
    cursor.execute('UPDATE users SET pet=? WHERE id=?', (pet_uuid, user_id))
    cursor.connection.commit()


def get_pet_info(user_id: int) -> list:
    return cursor.execute('SELECT * FROM users LEFT JOIN pet ON users.pet = pet.uuid WHERE id=?', (user_id, )).fetchone()


def give_admin_permissions(user_id: int) -> None:
    cursor.execute('UPDATE users SET is_admin=? WHERE id=?', (True, user_id))
    cursor.connection.commit()


def get_admins() -> list:
    return cursor.execute('SELECT * FROM users WHERE is_admin=True').fetchall()


def delete_admin(user_id: int) -> None:
    cursor.execute('UPDATE users SET is_admin=False WHERE id=?', (user_id, ))
    cursor.connection.commit()


def is_admin(user_id: int) -> bool:
    return bool(cursor.execute('SELECT is_admin FROM users WHERE id=?', (user_id, )).fetchone()[0])


# уменьшает кол-во еды и настроения у всех питомцев (вызывается 1 раз в 4 часа)
def change_count_food_and_mood() -> None:
    cursor.execute('UPDATE pet SET food=food - ?, mood=mood - ?', (config.food_consumption, config.mood_consumption))
    cursor.connection.commit()


# получаем список пользователей у которых показатель еды или настроения питомцев меньше 0
def check_pet_stats() -> list:
    users = cursor.execute(
        '''
        SELECT users.id FROM users JOIN pet ON users.pet = pet.uuid WHERE pet.food < 0 OR pet.mood < 0;
        '''
    ).fetchall()
    return users


def delete_pet(user_id: int) -> None:
    cursor.execute('UPDATE users SET pet = NULL WHERE id = ?;', (user_id,))
    cursor.execute('DELETE FROM pet WHERE uuid = (SELECT pet FROM users WHERE id = ?);', (user_id,))
    cursor.connection.commit()


def get_users() -> list:
    return cursor.execute('SELECT * FROM users').fetchall()
