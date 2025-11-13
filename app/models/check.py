from typing import List, Optional

class Form:
    """Простой DTO класс для формы проверки"""
    
    def __init__(self, 
                 form_id: str = "",
                 grades: List[int] = None,
                 errors_ids: List[int] = None,
                 id: int = None):
        self.id = id
        self.form_id = form_id
        self.grades = grades,
        self.errors_ids = errors_ids

    @staticmethod
    def get_grades_string(grades : List[int]) -> str:
        string_grades = ""
        for grade in grades:
            string_grades += str(grades) + ", "
        string_grades = string_grades[:-2]
        return string_grades
    
    @staticmethod
    def get_errors_string(grades : List[int]) -> str:
        string_grades = ""
        for grade in grades:
            string_grades += str(grades) + ", "
        string_grades = string_grades[:-2]
        return string_grades
    
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
        )
            