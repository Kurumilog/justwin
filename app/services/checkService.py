from app.db import Database
from app.models.form import Form
from app.models.check import Check
from typing import List

class CheckService:
    db = Database()
    
    @classmethod
    async def initialize(cls):
        await CheckService.db.initialize()
    
    @classmethod
    async def create_check(cls, form_id: str, grades: List[int], errors_ids: List[int], reviewer_id: str, addition: str = None) -> dict:
        _grades = Check.get_grades_string(grades)
        _errors_ids = Check.get_errors_string(errors_ids)
        return await CheckService.db.add('checks', form_id=form_id, grades=_grades, errors_ids=_errors_ids, reviewer_id = reviewer_id, addition=addition)
    
    @classmethod
    async def get_all_checks(cls) -> List[Check]:
        data = await CheckService.db.get_all('checks')
        checks = []
        for check_data in data:
            check = Check.from_dict(check_data)
            checks.append(check)
            # print(check.grades)
    
        return checks
    
    @classmethod
    async def get_check_by_id(cls, check_id: int) -> Form:
        check_dict = await CheckService.db.get_by_id('checks', check_id)
        return Check.from_dict(check_dict) 
    
    @classmethod
    async def delete_check(cls, check_id: int) -> bool:
        return await CheckService.db.delete('checks', check_id)