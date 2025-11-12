# dto/form_dto.py
from typing import List, Optional

class Form:
    """Простой DTO класс для формы"""
    
    def __init__(self, 
                 name: str = "",
                 tasks: List[int] = None,
                 addition: str = None,
                 id: int = None):
        self.id = id
        self.name = name
        self.tasks = tasks
        self.addition = addition

    @staticmethod
    def get_tasks_string(tasks : List[int]) -> str:
        string_tasks = ""
        for task in tasks:
            string_tasks += str(task) + ", "
        string_tasks = string_tasks[:-2]
        return string_tasks
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Form':
        """Создать из словаря"""
        tasks = []
        for letter in data.get('tasks'):
            if letter not in [' ', ',']:
                tasks.append(int(letter))
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            tasks=tasks, 
            addition=data.get('addition')
        )
            