# app/states/leader_states.py
from aiogram.fsm.state import State, StatesGroup


class LeaderStates(StatesGroup):
    """Состояния для работы руководителя бригады"""
    viewing_workers = State()  # Просмотр подчиненных
    viewing_errors = State()  # Просмотр ошибок бригады
