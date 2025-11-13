# service.py (со статическими методами)
from typing import List, Dict, Optional
from app.db import Database

class UserService:
    db = Database()
    
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
    
    @classmethod
    def get_access_level_name(cls, access_level: str) -> str:
        """Получить русское название уровня доступа"""
        return UserService.ACCESS_LEVEL_NAMES.get(access_level, access_level)
    
    @classmethod
    async def initialize(cls):
        await UserService.db.initialize()
    
    @classmethod
    async def create_user(cls, name: str, access_level: str = ACCESS_LEVEL_WORKER, available: bool = True) -> int:
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
    
    @classmethod
    async def get_user_access_level(cls, user_id: str) -> Optional[str]:
        """Получить уровень доступа пользователя"""
        body = await UserService.db.get_by_id("users", user_id)
        if body is not None:
            return body['access_level']
        return None
    
    @classmethod
    async def check_user_exist(cls, user_id: str) -> bool:
        """Проверить существование пользователя"""
        user = await UserService.db.get_by_id("users", user_id)
        return user is not None
    
    @classmethod
    async def get_user_by_name(cls, name: str) -> List[Dict]:
        """Найти пользователя по имени"""
        data = await UserService.db.query(
            "SELECT * FROM users WHERE name = ?", (name,)
        )
        return data
    
    @classmethod
    async def get_user_by_id(cls, user_id: str) -> Optional[Dict]:
        """Получить пользователя по ID"""
        return await UserService.db.get_by_id("users", user_id)
    
    @classmethod
    async def add_sample_users(cls) -> List[Dict]:
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
    
    @classmethod
    async def search_users_by_name(cls, name_part: str) -> List[Dict]:
        """Поиск пользователей по части имени"""
        return await UserService.db.query(
            "SELECT * FROM users WHERE name LIKE ?", 
            (f"%{name_part}%",)
        )
    
    @classmethod
    async def get_available_reviewers(cls) -> List[Dict]:
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
    
    @classmethod
    async def update_user_id_by_name(cls, name: str, user_id: str) -> bool:
        """Обновить user_id для пользователя по имени (PRIMARY KEY)"""
        result = await UserService.db.execute(
            "UPDATE users SET id = ? WHERE name = ?",
            (user_id, name)
        )
        return result > 0
    
    @classmethod
    async def update_user_available_status(cls, user_id: str, available_status: bool) -> int:
        return await UserService.db.update("users", user_id, available=available_status)
    
    @classmethod
    async def update_user_part_name(cls, user_id: str, part_name: str) -> int:
        result = await UserService.db.execute(
            "UPDATE users SET part_name = ? WHERE id = ?",
            (part_name, user_id)
        )
        return result > 0
    
    @classmethod
    async def update_user_part_name_by_name(cls, name: str, part_name: str) -> bool:
        """Обновить бригаду пользователя по имени (PRIMARY KEY)"""
        result = await UserService.db.execute(
            "UPDATE users SET part_name = ? WHERE name = ?",
            (part_name, name)
        )
        return result > 0
    
    @classmethod
    async def get_workers_by_part_name(cls, part_name: str) -> List[Dict]:
        """Получить всех работников (WORKER) конкретной бригады"""
        return await UserService.db.query(
            "SELECT * FROM users WHERE part_name = ? AND access_level = ? ORDER BY name",
            (part_name, UserService.ACCESS_LEVEL_WORKER)
        )
    
    @classmethod
    async def get_leaders(cls) -> List[Dict]:
        """Получить всех руководителей бригад"""
        return await UserService.db.query(
            "SELECT * FROM users WHERE access_level = ? ORDER BY name",
            (UserService.ACCESS_LEVEL_LEADER,)
        )
    
    @classmethod
    async def get_leader_by_part_name(cls, part_name: str) -> Optional[Dict]:
        """Получить руководителя конкретной бригады"""
        result = await UserService.db.query(
            "SELECT * FROM users WHERE part_name = ? AND access_level = ? LIMIT 1",
            (part_name, UserService.ACCESS_LEVEL_LEADER)
        )
        return result[0] if result else None
    
    @classmethod
    async def get_all_users(cls) -> List[Dict]:
        """Получить всех пользователей"""
        return await UserService.db.get_all("users")
    
    @classmethod
    async def update_user_access_level(cls, name: str, access_level: str) -> bool:
        """Обновить уровень доступа пользователя по имени (PRIMARY KEY)"""
        valid_levels = [
            UserService.ACCESS_LEVEL_ADMIN,
            UserService.ACCESS_LEVEL_MANAGER,
            UserService.ACCESS_LEVEL_OFFICE_WORKER,
            UserService.ACCESS_LEVEL_LEADER,
            UserService.ACCESS_LEVEL_WORKER
        ]
        if access_level not in valid_levels:
            raise ValueError(f"Неверный уровень доступа")
        
        result = await UserService.db.execute(
            "UPDATE users SET access_level = ? WHERE name = ?",
            (access_level, name)
        )
        return result > 0
    
    @classmethod
    async def assign_worker_to_brigade(cls, worker_name: str, part_name: str) -> bool:
        """Назначить работника в бригаду"""
        result = await UserService.db.execute(
            "UPDATE users SET part_name = ? WHERE name = ? AND access_level = ?",
            (part_name, worker_name, UserService.ACCESS_LEVEL_WORKER)
        )
        return result > 0
    
    @classmethod
    async def get_office_workers(cls) -> List[Dict]:
        """Получить всех офисных работников"""
        return await UserService.db.query(
            "SELECT * FROM users WHERE access_level = ? ORDER BY name",
            (UserService.ACCESS_LEVEL_OFFICE_WORKER,)
        )