# app/keyboards/task_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict


def get_task_management_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления задачами (для ADMIN и MANAGER)"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ Создать задачу", callback_data="task_create")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Список задач", callback_data="task_list")
    )
    builder.row(
        InlineKeyboardButton(text="🔍 Поиск задачи", callback_data="task_search")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад в кабинет", callback_data="admin_cabinet")
    )
    
    return builder.as_markup()


def get_task_list_keyboard(tasks: List[Dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком задач
    
    Args:
        tasks: список задач из базы данных
        
    Returns:
        InlineKeyboardMarkup со списком задач
    """
    builder = InlineKeyboardBuilder()
    
    for task in tasks:
        task_id = task.get('id')
        task_info = task.get('info', 'Без описания')
        # Ограничиваем длину текста кнопки
        button_text = task_info[:40] + "..." if len(task_info) > 40 else task_info
        
        builder.row(
            InlineKeyboardButton(
                text=f"📌 {button_text}",
                callback_data=f"task_view_{task_id}"
            )
        )
    
    # Кнопки навигации
    builder.row(
        InlineKeyboardButton(text="➕ Создать новую", callback_data="task_create")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="manage_tasks")
    )
    
    return builder.as_markup()


def get_task_actions_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура действий с конкретной задачей
    
    Args:
        task_id: ID задачи
        
    Returns:
        InlineKeyboardMarkup с действиями
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"task_edit_{task_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Удалить", callback_data=f"task_delete_{task_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ К списку задач", callback_data="task_list")
    )
    
    return builder.as_markup()


def get_task_confirm_delete_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения удаления задачи
    
    Args:
        task_id: ID задачи
        
    Returns:
        InlineKeyboardMarkup с подтверждением
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"task_delete_confirm_{task_id}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data=f"task_view_{task_id}")
    )
    
    return builder.as_markup()
