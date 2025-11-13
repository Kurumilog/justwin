# app/services/plannedCheckService.py
from app.db import Database
from typing import List, Optional
from datetime import datetime


class PlannedCheckService:
    db = Database()
    
    @classmethod
    async def initialize(cls):
        await PlannedCheckService.db.initialize()
    
    @classmethod
    async def create_planned_check(cls, time: str, form_id: int, reviewer_id: str) -> int:
        """
        Создать запланированную проверку
        
        Args:
            time: Время проверки в формате ISO (YYYY-MM-DD HH:MM:SS)
            form_id: ID формы (бригады/цеха)
            reviewer_id: Telegram ID проверяющего (office_worker)
        
        Returns:
            ID созданной записи
        """
        return await PlannedCheckService.db.add(
            "planned_checks",
            time=time,
            form_id=form_id,
            reviewer_id=reviewer_id
        )
    
    @classmethod
    async def get_all_planned_checks(cls) -> List[dict]:
        """Получить все запланированные проверки"""
        return await PlannedCheckService.db.get_all("planned_checks")
    
    @classmethod
    async def get_planned_check_by_id(cls, check_id: int) -> Optional[dict]:
        """Получить запланированную проверку по ID"""
        return await PlannedCheckService.db.get_by_id("planned_checks", check_id)
    
    @classmethod
    async def get_planned_checks_by_form(cls, form_id: int) -> List[dict]:
        """Получить все запланированные проверки для конкретной формы"""
        return await PlannedCheckService.db.query(
            "SELECT * FROM planned_checks WHERE form_id = ? ORDER BY time DESC",
            (form_id,)
        )
    
    @classmethod
    async def get_planned_checks_by_reviewer(cls, reviewer_id: str) -> List[dict]:
        """Получить все запланированные проверки для конкретного проверяющего"""
        return await PlannedCheckService.db.query(
            "SELECT * FROM planned_checks WHERE reviewer_id = ? ORDER BY time ASC",
            (reviewer_id,)
        )
    
    @classmethod
    async def update_planned_check_time(cls, check_id: int, time: str) -> bool:
        """Обновить время проверки"""
        return await PlannedCheckService.db.update("planned_checks", check_id, time=time)
    
    @classmethod
    async def update_planned_check_reviewer(cls, check_id: int, reviewer_id: str) -> bool:
        """Обновить проверяющего"""
        return await PlannedCheckService.db.update("planned_checks", check_id, reviewer_id=reviewer_id)
    
    @classmethod
    async def delete_planned_check(cls, check_id: int) -> bool:
        """Удалить запланированную проверку"""
        return await PlannedCheckService.db.delete("planned_checks", check_id)
    
    @classmethod
    async def get_upcoming_checks(cls, limit: int = 10) -> List[dict]:
        """
        Получить ближайшие запланированные проверки
        
        Args:
            limit: Максимальное количество проверок
        
        Returns:
            Список запланированных проверок
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return await PlannedCheckService.db.query(
            "SELECT * FROM planned_checks WHERE time >= ? ORDER BY time ASC LIMIT ?",
            (current_time, limit)
        )
