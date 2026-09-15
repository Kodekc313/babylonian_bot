import sqlite3
from typing import Optional, Tuple

DB_NAME = "cultists.db"

def init_db():
    """Инициализация базы данных и создание таблиц."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            artifacts_count INTEGER DEFAULT 0,
            last_action_date TEXT
        )
    """)
    
    # Таблица инвентаря (найденные артефакты/сигилы)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT,
            item_type TEXT, -- 'artifact', 'sigil', 'tarot'
            description TEXT,
            obtained_date TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("🗄️ База данных инициализирована.")

def get_user(user_id: int) -> Optional[Tuple]:
    """Получить данные пользователя."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def add_user(user_id: int, username: str):
    """Добавить нового пользователя."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username, xp, level) VALUES (?, ?, 0, 1)",
        (user_id, username)
    )
    conn.commit()
    conn.close()

def add_xp(user_id: int, amount: int) -> Tuple[int, int, bool]:
    """
    Добавить опыт пользователю.
    Возвращает: (новый_xp, новый_level, leveled_up)
    Формула уровня: Level * 100 XP для следующего уровня.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Получаем текущие данные
    cursor.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return 0, 1, False
    
    current_xp, current_level = result
    new_xp = current_xp + amount
    
    # Проверка на повышение уровня
    xp_needed = current_level * 100
    leveled_up = False
    new_level = current_level
    
    if new_xp >= xp_needed:
        new_level += 1
        leveled_up = True
        # Можно добавить рекурсию для множественных левелапов за раз, но пока просто +1
        
    cursor.execute(
        "UPDATE users SET xp = ?, level = ? WHERE user_id = ?",
        (new_xp, new_level, user_id)
    )
    conn.commit()
    conn.close()
    
    return new_xp, new_level, leveled_up

def add_item_to_inventory(user_id: int, item_name: str, item_type: str, description: str):
    """Добавить предмет в инвентарь."""
    from datetime import datetime
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inventory (user_id, item_name, item_type, description, obtained_date) VALUES (?, ?, ?, ?, ?)",
        (user_id, item_name, item_type, description, datetime.now().strftime("%Y-%m-%d"))
    )
    # Обновляем счетчик артефактов в профиле если это артефакт
    if item_type == 'artifact':
        cursor.execute("UPDATE users SET artifacts_count = artifacts_count + 1 WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()

def get_inventory(user_id: int, limit: int = 5):
    """Получить последние предметы из инвентаря."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT item_name, item_type, obtained_date FROM inventory WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    result = cursor.fetchall()
    conn.close()
    return result
