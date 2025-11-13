# app/keyboards/main_menu.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.services.userService import UserService


def get_main_menu_keyboard(access_level: str) -> InlineKeyboardMarkup:
    """
    Главное меню в зависимости от уровня доступа пользователя
    
    Args:
        access_level: уровень доступа пользователя
        
    Returns:
        InlineKeyboardMarkup с доступными опциями
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопки для ADMIN и MANAGER - рабочий кабинет
    if access_level in [UserService.ACCESS_LEVEL_ADMIN, UserService.ACCESS_LEVEL_MANAGER]:
        builder.row(
            InlineKeyboardButton(text="🏢 Рабочий кабинет", callback_data="admin_cabinet")
        )
        builder.row(
            InlineKeyboardButton(text="📊 Проверки", callback_data="checks_management")
        )
    
    # Кнопки для OFFICE_WORKER - проведение проверок
    if access_level == UserService.ACCESS_LEVEL_OFFICE_WORKER:
        builder.row(
            InlineKeyboardButton(text="✅ Провести проверку", callback_data="conduct_check")
        )
        builder.row(
            InlineKeyboardButton(text="� Мои проверки", callback_data="my_checks")
        )
    
    # Кнопки для LEADER и WORKER
    if access_level in [UserService.ACCESS_LEVEL_LEADER, UserService.ACCESS_LEVEL_WORKER]:
        builder.row(
            InlineKeyboardButton(text="📋 Информация", callback_data="info")
        )
    
    # Кнопка помощи для всех
    builder.row(
        InlineKeyboardButton(text="❓ Помощь", callback_data="help")
    )
    
    return builder.as_markup()


def get_admin_cabinet_keyboard(access_level: str) -> InlineKeyboardMarkup:
    """
    Рабочий кабинет для ADMIN и MANAGER
    
    Args:
        access_level: уровень доступа пользователя
        
    Returns:
        InlineKeyboardMarkup с административными функциями
    """
    builder = InlineKeyboardBuilder()
    
    # Управление задачами и формами (доступно ADMIN и MANAGER)
    builder.row(
        InlineKeyboardButton(text="📝 Управление задачами", callback_data="manage_tasks")
    )
    builder.row(
        InlineKeyboardButton(text="📄 Управление формами", callback_data="manage_forms")
    )
    
    # Управление пользователями (только для ADMIN)
    if access_level == UserService.ACCESS_LEVEL_ADMIN:
        builder.row(
            InlineKeyboardButton(text="👥 Управление пользователями", callback_data="manage_users")
        )
    
    # Отчеты и статистика
    builder.row(
        InlineKeyboardButton(text="📊 Отчеты и статистика", callback_data="reports")
    )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад в меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_back_button() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="◀️ Назад в меню", callback_data="main_menu")
    )
    return builder.as_markup()


def get_back_to_cabinet_button() -> InlineKeyboardMarkup:
    """Кнопка возврата в рабочий кабинет"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="◀️ Назад в кабинет", callback_data="admin_cabinet")
    )
    return builder.as_markup()
