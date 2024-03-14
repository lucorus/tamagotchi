import sqlite3


try:
    connection = sqlite3.connect('files.db', check_same_thread=False)

    cursor = connection.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS pet (
        uuid TEXT PRIMARY KEY,
        name TEXT,
        food INTEGER DEFAULT 5,
        mood INTEGER DEFAULT 100,
        max_food INTEGER DEFAULT 5,
        max_mood INTEGER DEFAULT 100
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
        id BIGINT PRIMARY KEY,
        food INTEGER DEFAULT 0, 
        pet TEXT REFERENCES pet(uuid) DEFAULT NULL,
        is_admin BOOL DEFAULT False,
        coins INTEGER DEFAULT 0
        )
        '''
    )

except Exception as ex:
    print(ex)
