from typing import List, Optional

class Check:
    """Простой DTO класс для формы проверки"""
    
    def __init__(self, 
                 form_id: str,
                 grades: List[int],
                 errors_ids: List[int],
                 reviewer_id: str,
                 addition: str = None):
        self.form_id = form_id
        self.grades = grades
        self.errors_ids = errors_ids
        self.addition = addition
        self.reviewer_id = reviewer_id

    @staticmethod
    def get_grades_string(grades : List[int]) -> str:
        string_grades = ""
        for grade in grades:
            string_grades += str(grade) + ", "
        string_grades = string_grades[:-2]
        return string_grades
    
    @staticmethod
    def get_errors_string(errors : List[int]) -> str:
        string_errors = ""
        for error in errors:
            string_errors += str(error) + ", "
        string_errors = string_errors[:-2]
        return string_errors
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Check':
        """Создать из словаря"""
        
        def parse_number_string(s: str) -> list[int]:
            if not s:
                return []
            # Разделяем по запятым, убираем пробелы, фильтруем пустые строки
            return [int(x.strip()) for x in s.split(',') if x.strip().isdigit()]
        
        grades_str = data.get('grades', '')
        errors_str = data.get('errors_ids', '')
        
        grades = parse_number_string(grades_str)
        errors_ids = parse_number_string(errors_str)
        
        return cls(
            form_id=data.get('form_id'),
            grades=grades,
            errors_ids=errors_ids,
            reviewer_id=data.get('reviewer_id', ''),
            addition=data.get('addition', ''),
        )
            