import sqlite3
import datetime
from datetime import datetime

current_time = datetime.now()

conn = sqlite3.connect('data/data.db')
cursor = conn.cursor()

def create_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            user_name TEXT,
            user_first_name TEXT,
            videos INTEGER,
            premium INTEGER DEFAULT 0
        )
    ''')
    conn.commit()

def add_user(user_id, user_name):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()
    if existing_user is None:
        cursor.execute('''
            INSERT INTO users (user_id, user_name)
            VALUES (?, ?)
        ''', (user_id, user_name))
        conn.commit()
        
def check_user(uid):
    cursor.execute(f'SELECT * FROM Users WHERE user_id = {uid}')
    user = cursor.fetchone()
    if user:
        return True
    return False
    