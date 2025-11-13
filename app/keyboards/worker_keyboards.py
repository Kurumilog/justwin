# app/keyboards/worker_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_worker_cabinet_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура личного кабинета работника"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🏭 Информация о бригаде", callback_data="worker_view_brigade_info")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Оценки бригады", callback_data="worker_view_grades")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Ошибки бригады", callback_data="worker_view_errors")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_worker_checks_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для просмотра проверок работника"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="worker_cabinet")
    )
    
    return builder.as_markup()
