# app/keyboards/check_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict


def get_check_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура меню проверок"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Провести новую проверку", callback_data="check_new")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Мои проверки", callback_data="check_my_list")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="check_stats")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад в меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_form_selection_keyboard(forms: List[Dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора формы для проверки
    
    Args:
        forms: список доступных форм
        
    Returns:
        InlineKeyboardMarkup с формами
    """
    builder = InlineKeyboardBuilder()
    
    for form in forms:
        form_id = form.get('id')
        form_name = form.get('name', 'Без названия')
        button_text = form_name[:40] + "..." if len(form_name) > 40 else form_name
        
        builder.row(
            InlineKeyboardButton(
                text=f"📄 {button_text}",
                callback_data=f"check_form_{form_id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="conduct_check")
    )
    
    return builder.as_markup()


def get_check_grade_keyboard(task_id: int, current_task_num: int, total_tasks: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для выставления оценки задаче
    
    Args:
        task_id: ID задачи
        current_task_num: номер текущей задачи
        total_tasks: общее количество задач
        
    Returns:
        InlineKeyboardMarkup с оценками
    """
    builder = InlineKeyboardBuilder()
    
    # Оценки
    builder.row(
        InlineKeyboardButton(text="✅ Выполнено", callback_data=f"check_grade_{task_id}_pass"),
        InlineKeyboardButton(text="❌ Не выполнено", callback_data=f"check_grade_{task_id}_fail")
    )
    
    # Информация о прогрессе
    progress_text = f"Задача {current_task_num} из {total_tasks}"
    builder.row(
        InlineKeyboardButton(text=progress_text, callback_data="check_progress_info")
    )
    
    # Отмена проверки
    builder.row(
        InlineKeyboardButton(text="🚫 Отменить проверку", callback_data="check_cancel")
    )
    
    return builder.as_markup()


def get_error_report_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для добавления ошибки к задаче
    
    Args:
        task_id: ID задачи
        
    Returns:
        InlineKeyboardMarkup с опциями
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📝 Добавить комментарий", callback_data=f"error_comment_{task_id}")
    )
    builder.row(
        InlineKeyboardButton(text="📷 Добавить фото", callback_data=f"error_photo_{task_id}")
    )
    builder.row(
        InlineKeyboardButton(text="✅ Продолжить без ошибки", callback_data=f"error_skip_{task_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data=f"check_grade_{task_id}_retry")
    )
    
    return builder.as_markup()


def get_check_complete_keyboard(check_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура после завершения проверки
    
    Args:
        check_id: ID завершенной проверки
        
    Returns:
        InlineKeyboardMarkup с опциями
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📄 Посмотреть отчет", callback_data=f"check_view_{check_id}")
    )
    builder.row(
        InlineKeyboardButton(text="✅ Провести еще одну", callback_data="check_new")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ В главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_check_list_keyboard(checks: List[Dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком проверок
    
    Args:
        checks: список проверок
        
    Returns:
        InlineKeyboardMarkup со списком
    """
    builder = InlineKeyboardBuilder()
    
    for check in checks:
        check_id = check.get('id')
        checked_at = check.get('checked_at', 'Неизвестно')
        form_name = check.get('form_name', 'Форма')
        
        # Форматируем дату
        date_str = checked_at.split()[0] if checked_at else "???"
        button_text = f"📋 {form_name[:25]} - {date_str}"
        
        builder.row(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"check_view_{check_id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="my_checks")
    )
    
    return builder.as_markup()


def get_check_cancel_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения отмены проверки"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да, отменить", callback_data="check_cancel_confirm"),
        InlineKeyboardButton(text="❌ Продолжить проверку", callback_data="check_cancel_abort")
    )
    
    return builder.as_markup()
