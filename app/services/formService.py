from app.db import Database
from app.models.form import Form
from typing import List, Optional

class FormService:
    db = Database()
    
    @classmethod
    async def initialize(cls):
        await FormService.db.initialize()
    
    @classmethod
    async def create_form(cls, name: str, tasks: List[int], addition: str = None) -> int:
        _tasks = Form.get_tasks_string(tasks)
        return await FormService.db.add("forms", name=name, tasks=_tasks, addition=addition)
    
    @classmethod
    async def get_all_forms(cls) -> List[dict]:
        data = await FormService.db.get_all("forms")
        return data
    
    @classmethod
    async def get_form_by_id(cls, form_id: int) -> Optional[dict]:
        return await FormService.db.get_by_id("forms", form_id)
    
    @classmethod
    async def update_form_name(cls, form_id: int, name: str) -> bool:
        return await FormService.db.update("forms", form_id, name=name)
    
    @classmethod
    async def update_form_addition(cls, form_id: int, addition: str) -> bool:
        return await FormService.db.update("forms", form_id, addition=addition)
    
    @classmethod
    async def update_form_tasks(cls, form_id: int, tasks: List[int]) -> bool:
        _tasks = Form.get_tasks_string(tasks)
        return await FormService.db.update("forms", form_id, tasks=_tasks)
    
    @classmethod
    async def delete_form(cls, form_id: int) -> bool:
        return await FormService.db.delete("forms", form_id)
    
    @classmethod
    def parse_tasks_string(cls, tasks_str: str) -> List[int]:
        """Преобразовать строку задач в список ID"""
        if not tasks_str:
            return []
        try:
            return [int(tid) for tid in tasks_str.split(",") if tid.strip()]
        except ValueError:
            return []
