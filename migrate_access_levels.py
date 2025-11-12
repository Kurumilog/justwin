"""
Скрипт миграции для преобразования access_level из INTEGER в TEXT
Старые значения:
- 0 -> 'admin'
- 1 -> 'manager'
- 2 -> 'office_worker'
- 3 -> 'leader'
- 4 -> 'worker'
"""

import asyncio
import aiosqlite
import os


async def migrate_access_levels():
    db_path = "app.db"
    
    if not os.path.exists(db_path):
        print("База данных не найдена. Миграция не требуется.")
        return
    
    print("Начало миграции базы данных...")
    
    # Маппинг старых значений на новые
    level_mapping = {
        0: 'admin',
        1: 'manager',
        2: 'office_worker',
        3: 'leader',
        4: 'worker'
    }
    
    async with aiosqlite.connect(db_path) as conn:
        # Проверяем, что таблица users существует
        cursor = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        table_exists = await cursor.fetchone()
        
        if not table_exists:
            print("Таблица users не найдена. Миграция не требуется.")
            return
        
        # Проверяем тип столбца access_level
        cursor = await conn.execute("PRAGMA table_info(users)")
        columns = await cursor.fetchall()
        
        access_level_column = None
        for col in columns:
            if col[1] == 'access_level':
                access_level_column = col
                break
        
        if not access_level_column:
            print("Столбец access_level не найден.")
            return
        
        column_type = access_level_column[2]  # Тип столбца
        print(f"Текущий тип столбца access_level: {column_type}")
        
        if column_type.upper() == 'TEXT':
            print("Миграция уже выполнена. access_level имеет тип TEXT.")
            return
        
        # Получаем все записи пользователей
        cursor = await conn.execute("SELECT name, access_level FROM users")
        users = await cursor.fetchall()
        
        if not users:
            print("Нет пользователей для миграции.")
        else:
            print(f"Найдено пользователей: {len(users)}")
        
        # Создаем новую таблицу с правильной структурой
        await conn.execute('''
            CREATE TABLE users_new (
                id TEXT,
                name TEXT PRIMARY KEY,
                access_level TEXT NOT NULL CHECK(access_level IN ('admin', 'manager', 'office_worker', 'leader', 'worker')),
                available BOOL NOT NULL
            )
        ''')
        
        # Копируем данные с преобразованием access_level
        for user in users:
            name = user[0]
            old_level = user[1]
            new_level = level_mapping.get(old_level, 'worker')
            
            # Получаем полную запись пользователя
            cursor = await conn.execute("SELECT id, name, available FROM users WHERE name = ?", (name,))
            full_user = await cursor.fetchone()
            
            if full_user:
                user_id, name, available = full_user
                await conn.execute(
                    "INSERT INTO users_new (id, name, access_level, available) VALUES (?, ?, ?, ?)",
                    (user_id, name, new_level, available)
                )
                print(f"Мигрирован пользователь: {name}, {old_level} -> {new_level}")
        
        # Удаляем старую таблицу и переименовываем новую
        await conn.execute("DROP TABLE users")
        await conn.execute("ALTER TABLE users_new RENAME TO users")
        
        await conn.commit()
        print("✅ Миграция успешно завершена!")


if __name__ == "__main__":
    asyncio.run(migrate_access_levels())
