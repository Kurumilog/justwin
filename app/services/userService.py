# service.py (со статическими методами)
from typing import List, Dict, Optional
from app.db import Database

class UserService:
    db = Database()
    initialized = False
    
    # Константы уровней доступа
    ACCESS_LEVEL_ADMIN = 'admin'
    ACCESS_LEVEL_MANAGER = 'manager'
    ACCESS_LEVEL_OFFICE_WORKER = 'office_worker'
    ACCESS_LEVEL_LEADER = 'leader'
    ACCESS_LEVEL_WORKER = 'worker'
    
    # Перевод уровней доступа на русский
    ACCESS_LEVEL_NAMES = {
        'admin': 'Администратор',
        'manager': 'Менеджер',
        'office_worker': 'Офисный работник',
        'leader': 'Руководитель',
        'worker': 'Работник'
    }
    
    @staticmethod
    def get_access_level_name(access_level: str) -> str:
        """Получить русское название уровня доступа"""
        return UserService.ACCESS_LEVEL_NAMES.get(access_level, access_level)
    
    @staticmethod
    async def initialize():
        """Инициализировать базу данных"""
        if not UserService.initialized:
            await UserService.db.initialize()
            UserService.initialized = True
    
    @staticmethod
    async def create_user(name: str, access_level: str, available: bool = True) -> int:
        """Создать нового пользователя
        
        Args:
            name: ФИО пользователя
            access_level: уровень доступа ('admin', 'manager', 'office_worker', 'leader', 'worker')
            available: доступность пользователя
        """
        valid_levels = [
            UserService.ACCESS_LEVEL_ADMIN,
            UserService.ACCESS_LEVEL_MANAGER,
            UserService.ACCESS_LEVEL_OFFICE_WORKER,
            UserService.ACCESS_LEVEL_LEADER,
            UserService.ACCESS_LEVEL_WORKER
        ]
        if access_level not in valid_levels:
            raise ValueError(f"Неверный уровень доступа. Допустимые значения: {', '.join(valid_levels)}")
        
        return await UserService.db.add('users', name=name, access_level=access_level, available=available)
    
    @staticmethod
    async def get_user_access_level(user_id: str) -> Optional[str]:
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
        return await UserService.db.get_by_id("users", user_id)
    
    @staticmethod
    async def add_sample_users() -> List[Dict]:
        """Добавить тестовых пользователей"""
        users_data = [
            {"name": "Даник", "access_level": UserService.ACCESS_LEVEL_MANAGER, "available": True},
            {"name": "Миша", "access_level": UserService.ACCESS_LEVEL_OFFICE_WORKER, "available": True},
            {"name": "Илья", "access_level": UserService.ACCESS_LEVEL_LEADER, "available": True},
        ]
        
        users = []
        for user_data in users_data:
            user_id = await UserService.create_user(**user_data)
            # Получаем созданного пользователя чтобы вернуть полные данные
            user = await UserService.get_user_by_id(user_id)
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
        """Получить доступных проверяющих (office_worker и выше)"""
        # Проверяющими могут быть office_worker, manager и admin
        allowed_levels = (
            UserService.ACCESS_LEVEL_ADMIN,
            UserService.ACCESS_LEVEL_MANAGER,
            UserService.ACCESS_LEVEL_OFFICE_WORKER
        )
        placeholders = ','.join(['?' for _ in allowed_levels])
        return await UserService.db.query(
            f"SELECT * FROM users WHERE available = 1 AND access_level IN ({placeholders}) ORDER BY id",
            allowed_levels
        )
    
    @staticmethod
    async def update_user_id_by_name(name: str, user_id: str) -> bool:
        """Обновить user_id для пользователя по имени (PRIMARY KEY)"""
        result = await UserService.db.execute(
            "UPDATE users SET id = ? WHERE name = ?",
            (user_id, name)
        )
        return result > 0