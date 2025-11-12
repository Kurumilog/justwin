# service.py
from typing import List, Dict, Optional
from app.db import Database

class UserService:
    db = Database()
    
    @staticmethod
    def get_user_access_level(user_id: str) -> int:
        body = UserService.db.get_by_id("users", user_id)
        if body is not None:
            return body[id]
        
    @staticmethod
    def check_user_exist(user_id: str) -> bool:
        id = UserService.db.get_by_id("users", user_id)
        if id is not None:
            return True
        else:
            return False
    
    def get_all_users() -> List[Dict]:
        """Получить всех пользователей"""
        return UserService.db.get_all('users')
    
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """Получить пользователя по ID"""
        return UserService.db.get_by_id('users', user_id)
    
    def get_user_by_email(email: str) -> Optional[Dict]:
        """Получить пользователя по email"""
        result = UserService.db.query("SELECT * FROM users WHERE email = ?", (email,))
        return result[0] if result else None
    
    def update_user(user_id: int, **kwargs) -> bool:
        """Обновить данные пользователя"""
        return UserService.db.update('users', user_id, **kwargs)
    
    def delete_user(user_id: int) -> bool:
        """Удалить пользователя"""
        return UserService.db.delete('users', user_id)
    
    def search_users(search_term: str) -> List[Dict]:
        """Поиск пользователей по имени или email"""
        return UserService.db.query(
            "SELECT * FROM users WHERE name LIKE ? OR email LIKE ?",
            (f"%{search_term}%", f"%{search_term}%")
        )
    
    def get_users_by_age_range(min_age: int, max_age: int) -> List[Dict]:
        """Получить пользователей по возрастному диапазону"""
        return UserService.db.query(
            "SELECT * FROM users WHERE age BETWEEN ? AND ? ORDER BY age",
            (min_age, max_age)
        )