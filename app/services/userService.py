# service.py
from typing import List, Dict, Optional
from app.db import Database

class UserService:
    db = Database()
    
    def get_user_access_level(self, user_id: str) -> int:
        body = self.db.get_by_id("users", user_id)
        if body is not None:
            return body[id]
        
    @staticmethod
    def check_user_exist(user_id: str) -> bool:
        id = UserService.db.get_by_id("users", user_id)
        if id is not None:
            return True
        else:
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Получить всех пользователей"""
        return self.db.get_all('users')
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя по ID"""
        return self.db.get_by_id('users', user_id)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Получить пользователя по email"""
        result = self.db.query("SELECT * FROM users WHERE email = ?", (email,))
        return result[0] if result else None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Обновить данные пользователя"""
        return self.db.update('users', user_id, **kwargs)
    
    def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        return self.db.delete('users', user_id)
    
    def search_users(self, search_term: str) -> List[Dict]:
        """Поиск пользователей по имени или email"""
        return self.db.query(
            "SELECT * FROM users WHERE name LIKE ? OR email LIKE ?",
            (f"%{search_term}%", f"%{search_term}%")
        )
    
    def get_users_by_age_range(self, min_age: int, max_age: int) -> List[Dict]:
        """Получить пользователей по возрастному диапазону"""
        return self.db.query(
            "SELECT * FROM users WHERE age BETWEEN ? AND ? ORDER BY age",
            (min_age, max_age)
        )