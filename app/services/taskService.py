from app.db import Database

class TaskService:
    db = Database()
    
    @staticmethod
    async def initialize():
        await TaskService.db.initialize()
    
    @staticmethod
    async def create_task(info: str) -> dict:
        return await TaskService.db.add('tasks', info=info)
    
    @staticmethod
    async def get_all_tasks():
        return await TaskService.db.get_all('tasks')
    
    @staticmethod
    async def get_task_by_id(task_id: str):
        return await TaskService.db.get_by_id('tasks', int(task_id))
    
    @staticmethod
    async def update_task(task_id: str, info: str) -> bool:
        return await TaskService.db.update('tasks', int(task_id), info=info)
    
    @staticmethod
    async def delete_task(task_id: str) -> bool:
        return await TaskService.db.delete('tasks', int(task_id))