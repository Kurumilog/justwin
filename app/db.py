# db.py
import aiosqlite
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_name: str = "app.db"):
        self.db_name = db_name
    
    async def initialize(self):
        """Инициализировать базу данных"""
        await self._create_tables()
    
    async def _create_tables(self):
        """Создать таблицы"""
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER,
                    name TEXT PRIMARY KEY,
                    access_level INTEGER NOT NULL,
                    available BOOL NOT NULL
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    info TEXT NOT NULL
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS forms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    tasks TEXT NOT NULL,
                    addition TEXT
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    comment TEXT NOT NULL,
                    photo_url TEXT
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    grades TEXT NOT NULL,
                    errors_ids TEXT,
                    reviewer_id INTEGER NOT NULL,
                    checked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (form_id) REFERENCES forms(id) ON DELETE CASCADE,
                    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS planned_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time DATETIME NOT NULL,
                    form_id INTEGER NOT NULL,
                    reviewer_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (form_id) REFERENCES forms(id) ON DELETE CASCADE,
                    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS form_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_id INTEGER NOT NULL,
                    task_id INTEGER NOT NULL,
                    task_order INTEGER NOT NULL,
                    FOREIGN KEY (form_id) REFERENCES forms(id) ON DELETE CASCADE,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    UNIQUE(form_id, task_id)
                )
            ''')
            
            await conn.commit()
    
    async def add(self, table: str, **data) -> int:
        """Добавить запись в таблицу"""
        async with aiosqlite.connect(self.db_name) as conn:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            cursor = await conn.execute(query, tuple(data.values()))
            await conn.commit()
            return cursor.lastrowid
    
    async def get_all(self, table: str) -> List[Dict]:
        """Получить все записи из таблицы"""
        async with aiosqlite.connect(self.db_name) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(f"SELECT * FROM {table}")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_by_id(self, table: str, item_id: int) -> Optional[Dict]:
        """Получить запись по ID"""
        async with aiosqlite.connect(self.db_name) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def update(self, table: str, item_id: int, **data) -> bool:
        """Обновить запись"""
        if not data:
            return False
            
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = list(data.values())
        values.append(item_id)
        
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", values)
            await conn.commit()
            return cursor.rowcount > 0
    
    async def delete(self, table: str, item_id: int) -> bool:
        """Удалить запись"""
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
            await conn.commit()
            return cursor.rowcount > 0
    
    async def query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """Выполнить произвольный SQL запрос"""
        async with aiosqlite.connect(self.db_name) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(sql, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def execute(self, sql: str, params: tuple = ()) -> int:
        """Выполнить SQL команду (без возврата данных)"""
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.execute(sql, params)
            await conn.commit()
            return cursor.rowcount