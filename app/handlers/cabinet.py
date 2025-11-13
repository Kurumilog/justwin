# app/handlers/cabinet.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.services.userService import UserService
from app.keyboards import get_admin_cabinet_keyboard, get_main_menu_keyboard

router = Router()


@router.callback_query(F.data == "admin_cabinet")
async def show_admin_cabinet(callback: CallbackQuery, state: FSMContext) -> None:
    """Показать рабочий кабинет для ADMIN и MANAGER"""
    # Очищаем любые активные состояния
    await state.clear()
    
    user_id = callback.from_user.id
    access_level = await UserService.get_user_access_level(str(user_id))
    
    # Проверяем права доступа
    if access_level not in [UserService.ACCESS_LEVEL_ADMIN, UserService.ACCESS_LEVEL_MANAGER]:
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    access_name = UserService.get_access_level_name(access_level)
    
    await callback.message.edit_text(
        f"🏢 <b>Рабочий кабинет</b>\n\n"
        f"Роль: {access_name}\n\n"
        f"Здесь вы можете управлять задачами, формами и просматривать отчеты.",
        reply_markup=get_admin_cabinet_keyboard(access_level),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "reports")
async def show_reports(callback: CallbackQuery) -> None:
    """Показать отчеты и статистику"""
    user_id = callback.from_user.id
    access_level = await UserService.get_user_access_level(str(user_id))
    
    if access_level not in [UserService.ACCESS_LEVEL_ADMIN, UserService.ACCESS_LEVEL_MANAGER]:
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    # TODO: Реализовать статистику
    await callback.message.edit_text(
        "📊 <b>Отчеты и статистика</b>\n\n"
        "🚧 Раздел находится в разработке\n\n"
        "Здесь будет:\n"
        "• Статистика проверок\n"
        "• Аналитика по задачам\n"
        "• Отчеты по сотрудникам\n"
        "• Графики и диаграммы",
        reply_markup=get_admin_cabinet_keyboard(access_level),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "manage_users")
async def show_manage_users(callback: CallbackQuery) -> None:
    """Управление пользователями (только для ADMIN) - переадресация"""
    user_id = callback.from_user.id
    access_level = await UserService.get_user_access_level(str(user_id))
    
    if access_level != UserService.ACCESS_LEVEL_ADMIN:
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    # Переадресуем на обработчик из admin.py
    from app.keyboards.admin_keyboards import get_admin_users_management_keyboard
    
    await callback.message.edit_text(
        "👥 <b>Управление пользователями</b>\n\n"
        "Здесь вы можете:\n"
        "• Создавать новых пользователей\n"
        "• Изменять уровни доступа\n"
        "• Назначать пользователей в бригады\n"
        "• Удалять пользователей",
        reply_markup=get_admin_users_management_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery) -> None:
    """Показать справку"""
    user_id = callback.from_user.id
    access_level = await UserService.get_user_access_level(str(user_id))
    
    help_text = "❓ <b>Справка</b>\n\n"
    
    if access_level in [UserService.ACCESS_LEVEL_ADMIN, UserService.ACCESS_LEVEL_MANAGER]:
        help_text += (
            "🏢 <b>Рабочий кабинет</b>\n"
            "• Управление задачами - создание и редактирование задач для проверок\n"
            "• Управление формами - создание форм проверок с набором задач\n"
            "• Отчеты - просмотр статистики и аналитики\n\n"
            "📊 <b>Проверки</b>\n"
            "• Просмотр всех проведенных проверок\n"
            "• Статистика по сотрудникам\n\n"
        )
    elif access_level == UserService.ACCESS_LEVEL_OFFICE_WORKER:
        help_text += (
            "✅ <b>Провести проверку</b>\n"
            "• Выберите форму для проверки\n"
            "• Оцените каждую задачу\n"
            "• Добавьте комментарии при необходимости\n\n"
            "📋 <b>Мои проверки</b>\n"
            "• История ваших проверок\n"
            "• Детали каждой проверки\n\n"
        )
    
    help_text += "Для возврата в главное меню используйте /menu"
    
    await callback.message.edit_text(
        help_text,
        reply_markup=get_main_menu_keyboard(access_level),
        parse_mode="HTML"
    )
    await callback.answer()
