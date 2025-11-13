# app/keyboards/admin_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict
from app.services.userService import UserService


def get_admin_users_management_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления пользователями для администратора"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ Создать пользователя", callback_data="admin_create_user")
    )
    builder.row(
        InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_list_users")
    )
    builder.row(
        InlineKeyboardButton(text="🔍 Поиск пользователя", callback_data="admin_search_user")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад в кабинет", callback_data="admin_cabinet")
    )
    
    return builder.as_markup()


def get_users_list_keyboard(users: List[Dict], action_prefix: str = "admin_edit_user") -> InlineKeyboardMarkup:
    """
    Клавиатура со списком пользователей
    
    Args:
        users: список пользователей
        action_prefix: префикс для callback_data
    """
    builder = InlineKeyboardBuilder()
    
    if users:
        for user in users:
            name = user.get('name', 'Без имени')
            access_level = user.get('access_level', '')
            access_name = UserService.get_access_level_name(access_level)
            
            # Иконки для уровней доступа
            icon = {
                'admin': '👑',
                'manager': '📊',
                'office_worker': '📋',
                'leader': '👔',
                'worker': '👷'
            }.get(access_level, '👤')
            
            builder.row(
                InlineKeyboardButton(
                    text=f"{icon} {name} ({access_name})",
                    callback_data=f"{action_prefix}_{name}"
                )
            )
    else:
        builder.row(
            InlineKeyboardButton(text="⚠️ Нет пользователей", callback_data="no_action")
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin_manage_users")
    )
    
    return builder.as_markup()


def get_access_level_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора уровня доступа"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👑 Администратор", callback_data=f"access_level_{UserService.ACCESS_LEVEL_ADMIN}")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Менеджер", callback_data=f"access_level_{UserService.ACCESS_LEVEL_MANAGER}")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Офисный работник", callback_data=f"access_level_{UserService.ACCESS_LEVEL_OFFICE_WORKER}")
    )
    builder.row(
        InlineKeyboardButton(text="👔 Руководитель бригады", callback_data=f"access_level_{UserService.ACCESS_LEVEL_LEADER}")
    )
    builder.row(
        InlineKeyboardButton(text="👷 Работник", callback_data=f"access_level_{UserService.ACCESS_LEVEL_WORKER}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Отмена", callback_data="admin_manage_users")
    )
    
    return builder.as_markup()


def get_user_edit_keyboard(user_name: str) -> InlineKeyboardMarkup:
    """Клавиатура для редактирования пользователя"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔑 Изменить уровень доступа", callback_data=f"admin_change_access_{user_name}")
    )
    builder.row(
        InlineKeyboardButton(text="🏭 Назначить в бригаду", callback_data=f"admin_assign_brigade_{user_name}")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Удалить пользователя", callback_data=f"admin_delete_user_{user_name}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ К списку", callback_data="admin_list_users")
    )
    
    return builder.as_markup()


def get_brigades_assignment_keyboard(forms: List[Dict], user_name: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора бригады при назначении
    
    Args:
        forms: список форм (бригад)
        user_name: имя пользователя для назначения
    """
    builder = InlineKeyboardBuilder()
    
    if forms:
        for form in forms:
            part_name = form.get('part_name', 'Без названия')
            builder.row(
                InlineKeyboardButton(
                    text=f"🏭 {part_name}",
                    callback_data=f"admin_set_brigade_{user_name}_{part_name}"
                )
            )
    else:
        builder.row(
            InlineKeyboardButton(text="⚠️ Нет бригад", callback_data="no_action")
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Отмена", callback_data=f"admin_edit_user_{user_name}")
    )
    
    return builder.as_markup()


def get_confirm_delete_user_keyboard(user_name: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления пользователя"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"admin_delete_confirm_{user_name}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data=f"admin_edit_user_{user_name}")
    )
    
    return builder.as_markup()
