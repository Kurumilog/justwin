# db.py
import sqlite3
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_name: str = "app.db"):
        self.db_name = db_name
        self._create_tables()
    
    def _get_connection(self):
        """Получить соединение с БД"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Чтобы получать строки как словари
        return conn
    
    def _create_tables(self):
        """Создать таблицы"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                access_level INTEGER NOT NULL,
                available BOOL NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                info TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                tasks TEXT NOT NULL,
                addition TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comment TEXT NOT NULL,
                photo_url TEXT
            )
        ''')

        cursor.execute('''
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

        cursor.execute('''
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

        # Дополнительная таблица для связи многие-ко-многим между формами и задачами
        cursor.execute('''
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
                    
                    
        conn.commit()
    
    # ОБЩИЕ МЕТОДЫ ДЛЯ РАБОТЫ С БД
    
    def add(self, table: str, **data) -> int:
        """Добавить запись в таблицу"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid
    
    def get_all(self, table: str) -> List[Dict]:
        """Получить все записи из таблицы"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_by_id(self, table: str, item_id: int) -> Optional[Dict]:
        """Получить запись по ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update(self, table: str, item_id: int, **data) -> bool:
        """Обновить запись"""
        if not data:
            return False
            
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = list(data.values())
        values.append(item_id)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", values)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete(self, table: str, item_id: int) -> bool:
        """Удалить запись"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """Выполнить произвольный SQL запрос"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]