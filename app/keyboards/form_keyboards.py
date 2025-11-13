# app/keyboards/form_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict


TASKS_PER_PAGE = 8  # Количество задач на одной странице


def get_form_management_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления формами (для ADMIN и MANAGER)"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ Создать форму", callback_data="form_create")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Список форм", callback_data="form_list")
    )
    builder.row(
        InlineKeyboardButton(text="🔍 Поиск формы", callback_data="form_search")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад в кабинет", callback_data="admin_cabinet")
    )
    
    return builder.as_markup()


def get_form_list_keyboard(forms: List[Dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком форм
    
    Args:
        forms: список форм из базы данных
        
    Returns:
        InlineKeyboardMarkup со списком форм
    """
    builder = InlineKeyboardBuilder()
    
    for form in forms:
        form_id = form.get('id')
        part_name = form.get('part_name', 'Без названия')
        # Ограничиваем длину текста кнопки
        button_text = part_name[:40] + "..." if len(part_name) > 40 else part_name
        
        builder.row(
            InlineKeyboardButton(
                text=f"📄 {button_text}",
                callback_data=f"form_view_{form_id}"
            )
        )
    
    # Кнопки навигации
    builder.row(
        InlineKeyboardButton(text="➕ Создать новую", callback_data="form_create")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="manage_forms")
    )
    
    return builder.as_markup()


def get_form_actions_keyboard(form_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура действий с конкретной формой
    
    Args:
        form_id: ID формы
        
    Returns:
        InlineKeyboardMarkup с действиями
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✏️ Изменить название", callback_data=f"form_edit_name_{form_id}")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Управление задачами", callback_data=f"form_tasks_{form_id}_0")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Удалить", callback_data=f"form_delete_{form_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ К списку форм", callback_data="form_list")
    )
    
    return builder.as_markup()


def get_form_confirm_delete_keyboard(form_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения удаления формы
    
    Args:
        form_id: ID формы
        
    Returns:
        InlineKeyboardMarkup с подтверждением
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"form_delete_confirm_{form_id}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data=f"form_view_{form_id}")
    )
    
    return builder.as_markup()


def get_form_task_selection_keyboard(
    tasks: List[Dict], 
    selected_task_ids: List[int], 
    form_id: int,
    page: int = 0
) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора задач для формы с пагинацией
    
    Args:
        tasks: список всех доступных задач
        selected_task_ids: список ID уже выбранных задач
        form_id: ID формы
        page: текущая страница (начиная с 0)
        
    Returns:
        InlineKeyboardMarkup с чекбоксами для задач
    """
    builder = InlineKeyboardBuilder()
    
    # Рассчитываем пагинацию
    total_tasks = len(tasks)
    total_pages = (total_tasks + TASKS_PER_PAGE - 1) // TASKS_PER_PAGE
    start_idx = page * TASKS_PER_PAGE
    end_idx = min(start_idx + TASKS_PER_PAGE, total_tasks)
    
    # Показываем задачи текущей страницы
    for task in tasks[start_idx:end_idx]:
        task_id = task.get('id')
        task_info = task.get('info', 'Без описания')
        is_selected = task_id in selected_task_ids
        
        # Добавляем галочку для выбранных задач
        prefix = "✅ " if is_selected else "⬜ "
        button_text = f"{prefix}{task_info[:35]}" + ("..." if len(task_info) > 35 else "")
        
        builder.row(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"form_task_toggle_{form_id}_{task_id}_{page}"
            )
        )
    
    # Кнопки пагинации (если есть несколько страниц)
    if total_pages > 1:
        pagination_buttons = []
        
        if page > 0:
            pagination_buttons.append(
                InlineKeyboardButton(text="◀️ Назад", callback_data=f"form_tasks_{form_id}_{page-1}")
            )
        
        pagination_buttons.append(
            InlineKeyboardButton(text=f"📄 {page+1}/{total_pages}", callback_data="page_info")
        )
        
        if page < total_pages - 1:
            pagination_buttons.append(
                InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"form_tasks_{form_id}_{page+1}")
            )
        
        builder.row(*pagination_buttons)
    
    # Информация о выбранных задачах
    selected_count = len(selected_task_ids)
    builder.row(
        InlineKeyboardButton(
            text=f"✅ Выбрано задач: {selected_count}",
            callback_data="selected_info"
        )
    )
    
    # Кнопки управления
    builder.row(
        InlineKeyboardButton(text="💾 Сохранить", callback_data=f"form_tasks_save_{form_id}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data=f"form_view_{form_id}")
    )
    
    return builder.as_markup()


def get_form_edit_options_keyboard(form_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора, что редактировать в форме
    
    Args:
        form_id: ID формы
        
    Returns:
        InlineKeyboardMarkup с опциями редактирования
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📝 Название", callback_data=f"form_edit_name_{form_id}")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Задачи", callback_data=f"form_tasks_{form_id}")
    )
    builder.row(
        InlineKeyboardButton(text="📄 Дополнительная информация", callback_data=f"form_edit_addition_{form_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data=f"form_view_{form_id}")
    )
    
    return builder.as_markup()
