# app/states/manager_states.py
from aiogram.fsm.state import State, StatesGroup


class ManagerStates(StatesGroup):
    """Состояния для работы менеджера"""
    planning_check_select_brigade = State()  # Выбор бригады для планирования проверки
    planning_check_select_date = State()  # Выбор даты проверки
    planning_check_select_time = State()  # Выбор времени проверки
    planning_check_select_reviewer = State()  # Выбор проверяющего
    planning_check_confirm = State()  # Подтверждение планирования
