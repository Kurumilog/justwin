# app/keyboards/leader_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict


def get_leader_cabinet_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура личного кабинета руководителя бригады"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👥 Мои подчиненные", callback_data="leader_view_workers")
    )
    builder.row(
        InlineKeyboardButton(text="⚠️ Ошибки бригады", callback_data="leader_view_errors")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_workers_list_keyboard(workers: List[Dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком подчиненных работников
    
    Args:
        workers: список работников бригады
    """
    builder = InlineKeyboardBuilder()
    
    if workers:
        for worker in workers:
            name = worker.get('name', 'Без имени')
            status = "✅" if worker.get('available') else "❌"
            builder.row(
                InlineKeyboardButton(
                    text=f"{status} {name}",
                    callback_data=f"worker_info_{worker.get('name')}"
                )
            )
    else:
        builder.row(
            InlineKeyboardButton(text="⚠️ Нет подчиненных", callback_data="no_action")
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="leader_cabinet")
    )
    
    return builder.as_markup()


def get_brigade_errors_keyboard(has_errors: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура для просмотра ошибок бригады"""
    builder = InlineKeyboardBuilder()
    
    if has_errors:
        builder.row(
            InlineKeyboardButton(text="📊 Статистика ошибок", callback_data="leader_errors_stats")
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="leader_cabinet")
    )
    
    return builder.as_markup()
