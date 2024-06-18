import uuid
import psycopg2
from aiogram.fsm.storage.memory import MemoryStorage
import config
import asyncpg
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

# Словарь, который хранит данные о всех активных действиях пользователей
# {user_id: ['название_действия', данные, которые нужны для данного действия/ничего], }
game_data = dict()
dp = Dispatcher(storage=MemoryStorage())
global bot
# connection = sqlite3.connect('files.db', check_same_thread=True)
# cursor = connection.cursor()
connection = psycopg2.connect(
            password=config.db_password,
            database=config.db_name,
            user=config.db_user
        )
connection.autocommit = True
# session = AiohttpSession(proxy=config.PROXY_URL)
# bot = Bot(token=config.token, session=session)
bot = Bot(config.token)


async def create_connect():
    try:
        conn = await asyncpg.connect(
            password=config.db_password,
            database=config.db_name,
            user=config.db_user,
        )
        return conn
    except Exception as ex:
        print(ex)


async def feed_pet(user_id: int, pet: list) -> None:
    conn = await create_connect()
    await conn.execute('UPDATE users SET food = food - 1 WHERE id=$1;', user_id)
    await conn.execute('UPDATE pet SET food = food + 1 WHERE uuid=$1;', pet[5])


async def add_coins(user_id: int, coins: int = 1) -> None:
    conn = await create_connect()
    await conn.execute('UPDATE users SET coins=coins+$1 WHERE id=$2;', coins, user_id)


async def add_mood(user_id: int, mood: int = 5) -> None:
    conn = await create_connect()
    pet = await get_pet_info(user_id)
    await conn.execute('UPDATE pet SET mood=mood+$1 WHERE uuid=$2;', mood, pet[2])
    await conn.execute('UPDATE pet SET mood=max_mood WHERE uuid=$1 AND mood>$2;', pet[2], pet[10])


async def buy_food(user_id: int, food_price: int) -> None:
    conn = await create_connect()
    await conn.execute('UPDATE users SET food = food + 1, coins = coins - $1 WHERE id=$2', food_price, user_id)


async def create_user(user_id: int) -> None:
    try:
        conn = await create_connect()
        await conn.execute('INSERT INTO users VALUES($1)', user_id)
    except Exception as ex:
        print(ex)


async def create_pet(user_id: int, name: str) -> None:
    conn = await create_connect()
    pet_uuid = str(uuid.uuid4())
    await conn.execute('INSERT INTO pet (uuid, name) VALUES($1, $2);', pet_uuid, name)
    await conn.execute('UPDATE users SET pet=$1 WHERE id=$2', pet_uuid, user_id)


async def get_user(user_id: int) -> list:
    conn = await create_connect()
    users = await conn.fetch('SELECT * FROM users WHERE id=$1', user_id)
    return users[0]


async def get_pet_info(user_id: int) -> list:
    conn = await create_connect()
    pet_info = await conn.fetch('SELECT * FROM users LEFT JOIN pet ON users.pet = pet.uuid WHERE id=$1', user_id)
    return pet_info[0]


async def give_admin_permissions(user_id: int) -> None:
    conn = await create_connect()
    await conn.execute('UPDATE users SET is_admin=$1 WHERE id=$2', True, user_id)


async def get_admins() -> list:
    conn = await create_connect()
    admins = await conn.fetch('SELECT * FROM users WHERE is_admin=True')
    return admins


async def delete_admin(user_id: int) -> None:
    conn = await create_connect()
    await conn.execute('UPDATE users SET is_admin=False WHERE id=$1', user_id)


async def is_admin(user_id: int) -> bool:
    conn = await create_connect()
    admin = await conn.fetch('SELECT is_admin FROM users WHERE id=$1', user_id,)
    return bool(admin[0])


# уменьшает кол-во еды и настроения у всех питомцев (вызывается 1 раз в 4 часа)
async def change_count_food_and_mood() -> None:
    conn = await create_connect()
    await conn.execute('UPDATE pet SET food=food - $1, mood=mood - $2', config.food_consumption, config.mood_consumption)


# получаем список пользователей у которых показатель еды или настроения питомцев меньше 0
async def check_pet_stats() -> list:
    conn = await create_connect()
    pet_stats = await conn.fetch('SELECT users.id FROM users JOIN pet ON users.pet = pet.uuid WHERE pet.food < 0 OR pet.mood < 0')
    return pet_stats


async def delete_pet(user_id: int) -> None:
    conn = await create_connect()
    await conn.execute('UPDATE users SET pet = NULL WHERE id = $1', user_id)
    await conn.execute('DELETE FROM pet WHERE uuid = (SELECT pet FROM users WHERE id = $1);', user_id)


# получаем данные всех пользователей
async def get_users() -> list:
    conn = await create_connect()
    users = await conn.fetch('SELECT * FROM users')
    return users[0]


# получаем список из id всех пользователей
async def get_users_id() -> list:
    conn = await create_connect()
    users = await conn.fetch('SELECT id FROM users')
    return users[0]


async def upgrade_stats(user_id: int, price: int, stat: str):
    pet_info = await get_pet_info(user_id)
    conn = await create_connect()
    if stat == 'food':
        improvement_points = 1
    else:
        improvement_points = 10
    await conn.execute(f'UPDATE pet SET max_{stat} = max_{stat} + {improvement_points} WHERE uuid = $1', pet_info[5])
    await conn.execute(f'UPDATE users SET coins = coins - {price} WHERE id=$1', user_id)
