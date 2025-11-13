# app/keyboards/manager_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict


def get_manager_cabinet_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура личного кабинета менеджера (расширенная версия админа)"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📋 Управление формами", callback_data="manage_forms")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Управление задачами", callback_data="manage_tasks")
    )
    builder.row(
        InlineKeyboardButton(text="📅 Планирование проверок", callback_data="manager_plan_checks")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Отчёты", callback_data="show_reports")
    )
    builder.row(
        InlineKeyboardButton(text="❓ Помощь", callback_data="show_help")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_brigades_list_keyboard(forms: List[Dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком бригад (форм) для планирования проверки
    
    Args:
        forms: список форм (бригад/цехов)
    """
    builder = InlineKeyboardBuilder()
    
    if forms:
        for form in forms:
            form_id = form.get('id')
            part_name = form.get('part_name', 'Без названия')
            builder.row(
                InlineKeyboardButton(
                    text=f"🏭 {part_name}",
                    callback_data=f"plan_check_brigade_{form_id}"
                )
            )
    else:
        builder.row(
            InlineKeyboardButton(text="⚠️ Нет бригад", callback_data="no_action")
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="checks_management")
    )
    
    return builder.as_markup()


def get_date_selection_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора даты проверки"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📅 Завтра (по умолчанию)", callback_data="plan_check_date_tomorrow")
    )
    builder.row(
        InlineKeyboardButton(text="📆 Выбрать другую дату", callback_data="plan_check_date_custom")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Отмена", callback_data="checks_management")
    )
    
    return builder.as_markup()


def get_reviewers_list_keyboard(reviewers: List[Dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком проверяющих (office_worker)
    
    Args:
        reviewers: список проверяющих
    """
    builder = InlineKeyboardBuilder()
    
    if reviewers:
        for reviewer in reviewers:
            name = reviewer.get('name', 'Без имени')
            user_id = reviewer.get('id', '')
            available = "✅" if reviewer.get('available') else "❌"
            
            builder.row(
                InlineKeyboardButton(
                    text=f"{available} {name}",
                    callback_data=f"plan_check_reviewer_{user_id}_{name}"
                )
            )
    else:
        builder.row(
            InlineKeyboardButton(text="⚠️ Нет доступных проверяющих", callback_data="no_action")
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Отмена", callback_data="checks_management")
    )
    
    return builder.as_markup()


def get_confirm_planned_check_keyboard(form_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения запланированной проверки"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"plan_check_confirm_{form_id}"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="checks_management")
    )
    
    return builder.as_markup()


def get_planned_checks_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для управления запланированными проверками"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📋 Список проверок", callback_data="manager_view_planned_checks")
    )
    builder.row(
        InlineKeyboardButton(text="➕ Новая проверка", callback_data="manager_plan_checks")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()
