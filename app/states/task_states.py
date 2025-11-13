# app/states/task_states.py
from aiogram.fsm.state import State, StatesGroup


class TaskStates(StatesGroup):
    """Состояния для работы с задачами"""
    waiting_for_task_info = State()  # Ожидание описания задачи при создании
    waiting_for_task_edit = State()  # Ожидание нового описания при редактировании
    waiting_for_search_query = State()  # Ожидание поискового запроса
