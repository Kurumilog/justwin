from app.db import Database
from typing import List

class FormService:
    db = Database()
    
    @staticmethod
    async def initialize():
        await FormService.db.initialize()
    
    @staticmethod
    async def create_form(name: str, _tasks: List[int], addition: str) -> dict:
        string_tasks = ""
        for task in _tasks:
            string_tasks += str(task) + ", "
        string_tasks = string_tasks[:-2]
        return await FormService.db.add('forms', name=name, tasks=string_tasks, addition=addition)
    
    @staticmethod
    async def get_all_tasks():
        return await FormService.db.get_all('tasks')
    
    @staticmethod
    async def get_task_by_id(task_id: str):
        return await FormService.db.get_by_id('tasks', int(task_id))
    
    @staticmethod
    async def update_task(task_id: str, info: str) -> bool:
        return await FormService.db.update('tasks', int(task_id), info=info)
    
    @staticmethod
    async def delete_task(task_id: str) -> bool:
        return await FormService.db.delete('tasks', int(task_id))