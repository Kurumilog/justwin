from app.db import Database
from app.models.form import Form
from typing import List

class FormService:
    db = Database()
    
    @classmethod
    async def initialize(cls):
        await FormService.db.initialize()
    
    @classmethod
    async def create_form(cls, name: str, tasks: List[int], addition: str) -> dict:
        _tasks = Form.get_tasks_string(tasks)
        return await FormService.db.add('forms', name=name, tasks=_tasks, addition=addition)
    
    @classmethod
    async def get_all_forms(cls) -> List[Form]:
        data = await FormService.db.get_all('forms')
        forms = []
        for form_data in data:
            form = Form.from_dict(form_data)
            forms.append(form)
    
        return forms
    
    @classmethod
    async def get_form_by_id(cls, task_id: int) -> Form:
        form_dict = await FormService.db.get_by_id('forms', task_id)
        return Form.from_dict(form_dict) 
    
    @classmethod
    async def delete_form(cls, task_id: int) -> bool:
        return await FormService.db.delete('forms', task_id)