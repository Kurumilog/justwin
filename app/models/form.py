from typing import List, Optional

class Form:
    """Простой DTO класс для формы"""
    
    def __init__(self, 
                 part_name: str = "",
                 tasks: List[int] = None,
                 id: int = None):
        self.id = id
        self.part_name = part_name
        self.tasks = tasks

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
        
        def parse_tasks_string(s: str) -> list[int]:
            if not s:
                return []
            return [int(x.strip()) for x in s.split(',') if x.strip().isdigit()]
        
        tasks_str = data.get('tasks', '')
        tasks = parse_tasks_string(tasks_str)
        
        return cls(
            id=data.get('id'),
            part_name=data.get('part_name', ''),
            tasks=tasks,
        )
            