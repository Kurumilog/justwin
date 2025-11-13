# app/states/form_states.py
from aiogram.fsm.state import State, StatesGroup


class FormStates(StatesGroup):
    """Состояния для работы с формами"""
    waiting_for_form_name = State()  # Ожидание названия формы при создании
    waiting_for_form_edit_name = State()  # Ожидание нового названия при редактировании
    waiting_for_form_addition = State()  # Ожидание дополнительной информации
    waiting_for_search_query = State()  # Ожидание поискового запроса
    selecting_tasks = State()  # Выбор задач для формы
