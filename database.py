import sqlite3

conn = sqlite3.connect('telegram_bot.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        chat_id INTEGER PRIMARY KEY
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        chat_id INTEGER PRIMARY KEY
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS channels (
        chat_id INTEGER PRIMARY KEY,
        channel_username TEXT
    )
''')

conn.commit()


async def add_user(chat_id):
    try:
        cursor.execute('INSERT INTO users (chat_id) VALUES (?)', (chat_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass


async def add_group(chat_id):
    try:
        cursor.execute('INSERT INTO groups (chat_id) VALUES (?)', (chat_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass


async def get_stat():
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM groups')
    group_count = cursor.fetchone()[0]

    return {'user_count': user_count, 'group_count': group_count}


async def add_channel(chat_id, channel_username):
    try:
        cursor.execute('INSERT INTO channels (chat_id, channel_username) VALUES (?, ?)', (chat_id, channel_username))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding channel: {e}")
        return False


async def del_channel(chat_id):
    try:
        cursor.execute('DELETE FROM channels WHERE chat_id = ?', (chat_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting channel: {e}")
        return False


def close_connection():
    conn.close()
