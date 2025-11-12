# service.py (со статическими методами)
from typing import List, Dict, Optional
from app.db import Database

class UserService:
    db = Database()
    initialized = False
    
    @staticmethod
    async def initialize():
        """Инициализировать базу данных"""
        if not UserService.initialized:
            await UserService.db.initialize()
            UserService.initialized = True
    
    @staticmethod
    async def create_user(name: str, access_level: int, available: bool = True) -> int:
        """Создать нового пользователя"""
        return await UserService.db.add('users', name=name, access_level=access_level, available=available)
    
    @staticmethod
    async def get_user_access_level(user_id: str) -> Optional[int]:
        """Получить уровень доступа пользователя"""
        body = await UserService.db.get_by_id("users", int(user_id))
        if body is not None:
            return body['access_level']
        return None
    
    @staticmethod
    async def check_user_exist(user_id: str) -> bool:
        """Проверить существование пользователя"""
        user = await UserService.db.get_by_id("users", int(user_id))
        return user is not None
    
    @staticmethod
    async def get_user_by_name(name: str) -> List[Dict]:
        """Найти пользователя по имени"""
        data = await UserService.db.query(
            "SELECT * FROM users WHERE name = ?", (name,)
        )
        return data
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[Dict]:
        """Получить пользователя по ID"""
        return await UserService.db.get_by_id("users", int(user_id))
    
    @staticmethod
    async def add_sample_users() -> List[Dict]:
        """Добавить тестовых пользователей"""
        users_data = [
            {"name": "Даник", "access_level": 1, "available": True},
            {"name": "Миша", "access_level": 2, "available": True},
            {"name": "Илья", "access_level": 3, "available": True},
        ]
        
        users = []
        for user_data in users_data:
            user_id = await UserService.create_user(**user_data)
            # Получаем созданного пользователя чтобы вернуть полные данные
            user = await UserService.get_user_by_id(str(user_id))
            if user:
                users.append(user)
        
        return users
    
    @staticmethod
    async def search_users_by_name(name_part: str) -> List[Dict]:
        """Поиск пользователей по части имени"""
        return await UserService.db.query(
            "SELECT * FROM users WHERE name LIKE ?", 
            (f"%{name_part}%",)
        )
    
    @staticmethod
    async def get_available_reviewers() -> List[Dict]:
        """Получить доступных проверяющих"""
        return await UserService.db.query(
            "SELECT * FROM users WHERE available = 1 AND access_level >= ? ORDER BY id",
            (2,)
        )