import sqlite3

conn = sqlite3.connect('data/data.db')
cursor = conn.cursor()


def get_users_count():
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    return count

def get_active_users_count():
    cursor.execute("SELECT COUNT(*) FROM users WHERE videos IS NOT NULL")
    count = cursor.fetchone()[0]
    return count


def get_premium_users_count():
    cursor.execute("SELECT COUNT(*) FROM users WHERE premium IS 1")
    count = cursor.fetchone()[0]
    return count

def get_all_user_ids():
    cursor.execute('SELECT user_id FROM users')
    user_ids = [row[0] for row in cursor.fetchall()]
    return user_ids

