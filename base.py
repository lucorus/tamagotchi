import sqlite3
import config
import uuid


def feed_pet(cursor: sqlite3.Cursor, user_id: int) -> None:
    pet = get_pet_info(cursor, user_id)
    if pet[1] > 0:
        cursor.execute(
            '''
            UPDATE pet
            SET food = CASE 
                WHEN food + 1 > max_food THEN food
                ELSE food + 1
            END WHERE uuid=?
            ''', (str(pet[2]), ))

        cursor.execute(
            '''
            UPDATE users SET food = CASE
                WHEN (SELECT food FROM pet WHERE uuid=?) = ? THEN food
                ELSE food - 1
            END WHERE id=?
            ''', (str(pet[2]), str(pet[9]), user_id)
        )
        cursor.connection.commit()


def add_coins(cursor: sqlite3.Cursor, user_id: int, coins: int = 1) -> None:
    cursor.execute('UPDATE users SET coins=coins+? WHERE id=?;', (coins, user_id))
    cursor.connection.commit()


def add_mood(cursor: sqlite3.Cursor, user_id: int, mood: int = 5) -> None:
    pet = get_pet_info(cursor, user_id)
    cursor.execute('UPDATE pet SET mood=mood+? WHERE uuid=?;', (mood, pet[2]))
    cursor.execute('UPDATE pet SET mood=max_mood WHERE uuid=? AND mood>?', (pet[2], pet[10]))
    cursor.connection.commit()


def buy_food(cursor: sqlite3.Cursor, user_id: int):
    cursor.execute('UPDATE users SET food = food + 1, coins = coins - 1 WHERE id=?', (user_id, ))
    cursor.connection.commit()


def create_pet(cursor: sqlite3.Cursor, user_id: int, name: str) -> None:
    pet_uuid = str(uuid.uuid4())
    cursor.execute('INSERT INTO pet (uuid, name) VALUES(?, ?);', (pet_uuid, name))
    cursor.execute('UPDATE users SET pet=? WHERE id=?', (pet_uuid, user_id))
    cursor.connection.commit()


def get_pet_info(cursor: sqlite3.Cursor, user_id: int) -> list:
    return cursor.execute('SELECT * FROM users LEFT JOIN pet ON users.pet = pet.uuid WHERE id=?', (user_id, )).fetchone()


def get_admin_status(cursor: sqlite3.Cursor, user_id: int) -> None:
    cursor.execute('UPDATE users SET is_admin=? WHERE id=?', (True, user_id))
    cursor.connection.commit()


def is_admin(cursor: sqlite3.Cursor, user_id: int) -> bool:
    return bool(cursor.execute('SELECT is_admin FROM users WHERE id=?', (user_id, )).fetchone()[0])


# уменьшает кол-во еды и настроения у всех питомцев (вызывается 1 раз в 4 часа)
def change_count_food_and_mood(cursor: sqlite3.Cursor) -> None:
    cursor.execute('UPDATE pet SET food=food - ?, mood=mood - ?', (config.food_consumption, config.mood_consumption))
    cursor.connection.commit()


# получаем список пользователей у которых показатель еды или настроения питомцев меньше 0
def check_pet_stats(cursor: sqlite3.Cursor) -> list:
    users = cursor.execute(
        '''
        SELECT users.id FROM users JOIN pet ON users.pet = pet.uuid WHERE pet.food < 0 OR pet.mood < 0;
        '''
    ).fetchall()
    return users


def delete_pet(cursor: sqlite3.Cursor, user_id: int) -> None:
    cursor.execute('UPDATE users SET pet = NULL WHERE id = ?;', (user_id,))
    cursor.execute('DELETE FROM pet WHERE uuid = (SELECT pet FROM users WHERE id = ?);', (user_id,))
    cursor.connection.commit()
