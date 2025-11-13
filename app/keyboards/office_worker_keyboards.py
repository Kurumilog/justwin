# app/keyboards/office_worker_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_task_check_keyboard(task_id: int, task_num: int, total_tasks: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для проверки задачи (ОК/Не ОК)
    
    Args:
        task_id: ID задачи
        task_num: номер текущей задачи
        total_tasks: общее количество задач
        
    Returns:
        InlineKeyboardMarkup с кнопками ОК/Не ОК
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопки ОК и Не ОК
    builder.row(
        InlineKeyboardButton(
            text="✅ ОК",
            callback_data=f"task_check_ok_{task_id}"
        ),
        InlineKeyboardButton(
            text="❌ Не ОК",
            callback_data=f"task_check_fail_{task_id}"
        )
    )
    
    # Информация о прогрессе
    progress_text = f"📊 {task_num}/{total_tasks}"
    builder.row(
        InlineKeyboardButton(
            text=progress_text,
            callback_data="check_progress_info"
        )
    )
    
    return builder.as_markup()


def get_error_options_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для добавления ошибки к задаче
    
    Args:
        task_id: ID задачи
        
    Returns:
        InlineKeyboardMarkup с опциями добавления ошибки
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📝 Добавить комментарий",
            callback_data=f"error_add_comment_{task_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📷 Добавить фото",
            callback_data=f"error_add_photo_{task_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="✅ Продолжить без ошибки",
            callback_data=f"error_skip_{task_id}"
        )
    )
    
    return builder.as_markup()


def get_error_confirm_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения ошибки
    
    Args:
        task_id: ID задачи
        
    Returns:
        InlineKeyboardMarkup с подтверждением
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✅ Сохранить ошибку",
            callback_data=f"error_save_{task_id}"
        ),
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data=f"error_cancel_{task_id}"
        )
    )
    
    return builder.as_markup()


def get_check_complete_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после завершения проверки"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="◀️ В главное меню",
            callback_data="check_back_to_menu"
        )
    )
    
    return builder.as_markup()

