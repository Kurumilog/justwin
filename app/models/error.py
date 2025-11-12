from typing import List, Optional

class Error:
    """Простой DTO класс для формы"""
    
    def __init__(self, 
                 id: int = None,
                 comment: str = None,
                 photo_url: str = None,
                 ):
        self.id = id
        self.comment = comment
        self.photo_url = photo_url

    @classmethod
    def from_dict(cls, data: dict) -> 'Error':
        return cls(
            id=data.get('id'),
            comment=data.get('comment'),
            photo_url=data.get('photo_url')
        )