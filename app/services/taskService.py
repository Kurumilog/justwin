from app.db import Database

class TaskService:
    db = Database()
    
    @classmethod
    async def initialize(cls):
        await TaskService.db.initialize()
    
    @classmethod
    async def create_task(cls, info: str) -> dict:
        return await TaskService.db.add('tasks', info=info)
    
    @classmethod
    async def get_all_tasks(cls):
        return await TaskService.db.get_all('tasks')
    
    @classmethod
    async def get_task_by_id(cls, task_id: int):
        return await TaskService.db.get_by_id('tasks', task_id)
    
    @classmethod
    async def update_task(cls, task_id: int, info: str) -> bool:
        return await TaskService.db.update('tasks', task_id, info=info)
    
    @classmethod
    async def delete_task(cls, task_id: int) -> bool:
        return await TaskService.db.delete('tasks', task_id)