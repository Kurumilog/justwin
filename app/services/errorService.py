from app.db import Database
from app.models.error import Error

class ErrorService:
    db = Database()
    
    @classmethod
    async def initialize(cls):
        await ErrorService.db.initialize()
    
    @classmethod
    async def create_error(cls, comment: str, photo_url: str = None) -> int:
        """Создать ошибку и вернуть её ID"""
        return await ErrorService.db.add('errors', comment=comment, photo_url=photo_url)
    
    @classmethod
    async def get_all_errors(cls):
        data = await ErrorService.db.get_all('errors')
        errors = []
        for error_data in data:
            error = Error.from_dict(error_data)
            errors.append(error)
    
        return errors

    
    @classmethod
    async def get_error_by_id(cls, error_id: int) -> Error:
        error_dict = await ErrorService.db.get_by_id('errors', error_id)
        return Error.from_dict(error_dict) 
    
    @classmethod
    async def update_error(cls, error_id: int, comment: str, photo_url: str) -> bool:
        return await ErrorService.db.update('errors', error_id, comment=comment, photo_url=photo_url)
    
    @classmethod
    async def delete_task(cls, error_id: str) -> bool:
        return await ErrorService.db.delete('errors', error_id)