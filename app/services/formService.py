from app.db import Database
from app.models.form import Form
from typing import List

class FormService:
    db = Database()
    
    @classmethod
    async def initialize(cls):
        await FormService.db.initialize()
    
    @classmethod
    async def create_form(cls, part_name: str, tasks: List[int]) -> dict:
        _tasks = Form.get_tasks_string(tasks)
        return await FormService.db.add('forms', part_name=part_name, tasks=_tasks)
    
    @classmethod
    async def get_all_forms(cls) -> List[Form]:
        data = await FormService.db.get_all('forms')
        forms = []
        for form_data in data:
            form = Form.from_dict(form_data)
            forms.append(form)
    
        return forms
    
    @classmethod
    async def get_form_by_id(cls, form_id: int) -> Form:
        form_dict = await FormService.db.get_by_id('forms', form_id)
        return Form.from_dict(form_dict) 
    
    @classmethod
    async def delete_form(cls, form_id: int) -> bool:
        return await FormService.db.delete('forms', form_id)