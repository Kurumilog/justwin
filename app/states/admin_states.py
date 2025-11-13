# app/states/admin_states.py
from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Состояния для работы администратора"""
    manage_users_select_user = State()  # Выбор пользователя
    manage_users_edit_access_level = State()  # Изменение уровня доступа
    manage_users_assign_brigade = State()  # Назначение в бригаду
    create_user_enter_name = State()  # Ввод имени нового пользователя
    create_user_select_access_level = State()  # Выбор уровня доступа
    create_user_assign_brigade = State()  # Назначение в бригаду (опционально)
