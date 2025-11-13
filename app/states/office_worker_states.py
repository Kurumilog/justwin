# app/states/office_worker_states.py
from aiogram.fsm.state import State, StatesGroup


class CheckStates(StatesGroup):
    """Состояния для процесса проверки office_worker"""
    checking_tasks = State()  # Процесс проверки задач
    adding_error_comment = State()  # Добавление комментария к ошибке
    adding_error_photo = State()  # Добавление фото к ошибке

