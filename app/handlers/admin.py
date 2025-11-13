# app/handlers/admin.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.services.userService import UserService
from app.services.formService import FormService
from app.states.admin_states import AdminStates
from app.keyboards.admin_keyboards import (
    get_admin_users_management_keyboard,
    get_users_list_keyboard,
    get_access_level_keyboard,
    get_user_edit_keyboard,
    get_brigades_assignment_keyboard,
    get_confirm_delete_user_keyboard
)

router = Router()


async def check_admin_rights(user_id: int) -> bool:
    """Проверка прав ADMIN"""
    access_level = await UserService.get_user_access_level(str(user_id))
    return access_level == UserService.ACCESS_LEVEL_ADMIN


@router.callback_query(F.data == "admin_manage_users")
async def show_users_management(callback: CallbackQuery, state: FSMContext) -> None:
    """Показать меню управления пользователями"""
    await state.clear()
    
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
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


@router.callback_query(F.data == "admin_create_user")
async def create_user_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать создание нового пользователя"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    await state.set_state(AdminStates.create_user_enter_name)
    await callback.message.edit_text(
        "➕ <b>Создание нового пользователя</b>\n\n"
        "Введите ФИО пользователя:\n\n"
        "<i>Пример: Иван Иванов</i>",
        reply_markup=get_admin_users_management_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminStates.create_user_enter_name, F.text)
async def create_user_enter_name(message: Message, state: FSMContext) -> None:
    """Обработка ввода имени пользователя"""
    name = message.text.strip()
    
    if len(name) < 3:
        await message.answer(
            "❌ ФИО слишком короткое. Минимум 3 символа.\n"
            "Попробуйте еще раз:"
        )
        return
    
    # Проверяем, существует ли уже пользователь с таким именем
    existing_users = await UserService.get_user_by_name(name)
    if existing_users:
        await message.answer(
            f"❌ <b>Пользователь с таким ФИО уже существует!</b>\n\n"
            f"ФИО: {name}\n\n"
            f"Пожалуйста, введите другое ФИО:",
            parse_mode="HTML"
        )
        return
    
    # Сохраняем имя и переходим к выбору уровня доступа
    await state.update_data(user_name=name)
    await state.set_state(AdminStates.create_user_select_access_level)
    
    await message.answer(
        f"✅ ФИО принято: <b>{name}</b>\n\n"
        f"Теперь выберите уровень доступа:",
        reply_markup=get_access_level_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("access_level_"), AdminStates.create_user_select_access_level)
async def create_user_select_access_level(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработка выбора уровня доступа при создании"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    access_level = callback.data.split("_", 2)[2]
    data = await state.get_data()
    user_name = data.get('user_name')
    
    # Создаем пользователя
    try:
        await UserService.create_user(
            name=user_name,
            access_level=access_level,
            available=True
        )
        
        access_name = UserService.get_access_level_name(access_level)
        
        await state.clear()
        await callback.message.edit_text(
            f"✅ <b>Пользователь успешно создан!</b>\n\n"
            f"<b>ФИО:</b> {user_name}\n"
            f"<b>Уровень доступа:</b> {access_name}\n"
            f"<b>Статус:</b> Доступен\n\n"
            f"Пользователь может зарегистрироваться в боте с помощью команды /register",
            reply_markup=get_admin_users_management_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("Пользователь создан!", show_alert=False)
    except Exception as e:
        await state.clear()
        await callback.message.edit_text(
            f"❌ <b>Ошибка при создании пользователя</b>\n\n"
            f"{str(e)}",
            reply_markup=get_admin_users_management_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()


@router.callback_query(F.data == "admin_list_users")
async def list_users(callback: CallbackQuery, state: FSMContext) -> None:
    """Показать список всех пользователей"""
    await state.clear()
    
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    users = await UserService.get_all_users()
    
    if not users:
        await callback.message.edit_text(
            "👥 <b>Список пользователей</b>\n\n"
            "Пользователей пока нет. Создайте первого пользователя!",
            reply_markup=get_admin_users_management_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            f"👥 <b>Список пользователей</b> ({len(users)} чел.)\n\n"
            f"Выберите пользователя для редактирования:",
            reply_markup=get_users_list_keyboard(users),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("admin_edit_user_"))
async def edit_user(callback: CallbackQuery, state: FSMContext) -> None:
    """Показать меню редактирования пользователя"""
    await state.clear()
    
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    user_name = callback.data.split("_", 3)[3]
    
    # Получаем информацию о пользователе
    users = await UserService.get_user_by_name(user_name)
    if not users:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    user = users[0]
    access_level = user.get('access_level', '')
    access_name = UserService.get_access_level_name(access_level)
    telegram_id = user.get('id', 'не привязан')
    part_name = user.get('part_name', 'Не назначена')
    available = user.get('available', False)
    
    await callback.message.edit_text(
        f"✏️ <b>Редактирование пользователя</b>\n\n"
        f"<b>ФИО:</b> {user_name}\n"
        f"<b>Telegram ID:</b> {telegram_id}\n"
        f"<b>Уровень доступа:</b> {access_name}\n"
        f"<b>Бригада:</b> {part_name}\n"
        f"<b>Статус:</b> {'✅ Доступен' if available else '❌ Недоступен'}\n\n"
        f"Что вы хотите изменить?",
        reply_markup=get_user_edit_keyboard(user_name),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_change_access_"))
async def change_access_level_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать изменение уровня доступа"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    user_name = callback.data.split("_", 3)[3]
    
    await state.update_data(user_name=user_name)
    await state.set_state(AdminStates.manage_users_edit_access_level)
    
    await callback.message.edit_text(
        f"🔑 <b>Изменение уровня доступа</b>\n\n"
        f"<b>Пользователь:</b> {user_name}\n\n"
        f"Выберите новый уровень доступа:",
        reply_markup=get_access_level_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("access_level_"), AdminStates.manage_users_edit_access_level)
async def change_access_level_process(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработка изменения уровня доступа"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    access_level = callback.data.split("_", 2)[2]
    data = await state.get_data()
    user_name = data.get('user_name')
    
    # Обновляем уровень доступа
    success = await UserService.update_user_access_level(user_name, access_level)
    
    await state.clear()
    
    if success:
        access_name = UserService.get_access_level_name(access_level)
        await callback.message.edit_text(
            f"✅ <b>Уровень доступа обновлен!</b>\n\n"
            f"<b>Пользователь:</b> {user_name}\n"
            f"<b>Новый уровень:</b> {access_name}",
            reply_markup=get_user_edit_keyboard(user_name),
            parse_mode="HTML"
        )
        await callback.answer("Уровень доступа изменен!", show_alert=False)
    else:
        await callback.message.edit_text(
            "❌ Ошибка при обновлении уровня доступа",
            reply_markup=get_admin_users_management_keyboard()
        )
        await callback.answer()


@router.callback_query(F.data.startswith("admin_assign_brigade_"))
async def assign_brigade_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать назначение в бригаду"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    user_name = callback.data.split("_", 3)[3]
    
    # Получаем список форм (бригад)
    forms = await FormService.get_all_forms()
    
    if not forms:
        await callback.message.edit_text(
            "⚠️ <b>Нет доступных бригад</b>\n\n"
            "Сначала создайте формы (бригады) в разделе управления формами.",
            reply_markup=get_user_edit_keyboard(user_name),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    await state.update_data(user_name=user_name)
    await state.set_state(AdminStates.manage_users_assign_brigade)
    
    await callback.message.edit_text(
        f"🏭 <b>Назначение в бригаду</b>\n\n"
        f"<b>Пользователь:</b> {user_name}\n\n"
        f"Выберите бригаду:",
        reply_markup=get_brigades_assignment_keyboard(forms, user_name),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_set_brigade_"))
async def assign_brigade_process(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработка назначения в бригаду"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    parts = callback.data.split("_", 3)
    # Формат: admin_set_brigade_UserName_PartName
    # Нужно разделить UserName и PartName
    combined = parts[3]
    
    data = await state.get_data()
    user_name = data.get('user_name')
    
    # part_name - всё после user_name_
    part_name = combined.split(f"{user_name}_", 1)[1] if f"{user_name}_" in combined else combined
    
    # Обновляем бригаду пользователя (по имени, т.к. name - PRIMARY KEY)
    success = await UserService.update_user_part_name_by_name(user_name, part_name)
    
    await state.clear()
    
    if success:
        await callback.message.edit_text(
            f"✅ <b>Пользователь назначен в бригаду!</b>\n\n"
            f"<b>Пользователь:</b> {user_name}\n"
            f"<b>Бригада:</b> {part_name}",
            reply_markup=get_user_edit_keyboard(user_name),
            parse_mode="HTML"
        )
        await callback.answer("Назначение выполнено!", show_alert=False)
    else:
        await callback.message.edit_text(
            "❌ Ошибка при назначении в бригаду",
            reply_markup=get_admin_users_management_keyboard()
        )
        await callback.answer()


@router.callback_query(F.data.startswith("admin_delete_user_") & ~F.data.contains("confirm"))
async def delete_user_ask(callback: CallbackQuery) -> None:
    """Запросить подтверждение удаления пользователя"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    user_name = callback.data.split("_", 3)[3]
    
    # Получаем информацию о пользователе
    users = await UserService.get_user_by_name(user_name)
    if not users:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    user = users[0]
    access_name = UserService.get_access_level_name(user.get('access_level', ''))
    
    await callback.message.edit_text(
        f"⚠️ <b>Удаление пользователя</b>\n\n"
        f"<b>ФИО:</b> {user_name}\n"
        f"<b>Уровень доступа:</b> {access_name}\n\n"
        f"Вы уверены, что хотите удалить этого пользователя?\n"
        f"<i>Это действие нельзя отменить!</i>",
        reply_markup=get_confirm_delete_user_keyboard(user_name),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_delete_confirm_"))
async def delete_user_confirm(callback: CallbackQuery) -> None:
    """Подтверждение удаления пользователя"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    user_name = callback.data.split("_", 3)[3]
    
    # Удаляем пользователя (по имени, т.к. name - PRIMARY KEY)
    success = await UserService.db.execute(
        "DELETE FROM users WHERE name = ?",
        (user_name,)
    )
    
    if success:
        await callback.message.edit_text(
            f"✅ <b>Пользователь удален!</b>\n\n"
            f"ФИО: {user_name}",
            reply_markup=get_admin_users_management_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("Пользователь удален", show_alert=False)
    else:
        await callback.answer("❌ Ошибка при удалении пользователя", show_alert=True)


@router.callback_query(F.data == "admin_search_user")
async def search_user_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать поиск пользователя"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    await state.set_state(AdminStates.manage_users_select_user)
    await callback.message.edit_text(
        "🔍 <b>Поиск пользователя</b>\n\n"
        "Введите ФИО или часть ФИО для поиска:",
        reply_markup=get_admin_users_management_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminStates.manage_users_select_user, F.text)
async def search_user_process(message: Message, state: FSMContext) -> None:
    """Обработка поиска пользователя"""
    query = message.text.strip()
    
    users = await UserService.search_users_by_name(query)
    
    await state.clear()
    
    if not users:
        await message.answer(
            f"🔍 По запросу «{query}» ничего не найдено",
            reply_markup=get_admin_users_management_keyboard()
        )
    else:
        await message.answer(
            f"🔍 Найдено пользователей: {len(users)}\n\n"
            f"Выберите пользователя:",
            reply_markup=get_users_list_keyboard(users)
        )


# Обработчик для информационной кнопки
@router.callback_query(F.data == "no_action")
async def no_action_handler(callback: CallbackQuery) -> None:
    """Обработка информационных кнопок"""
    await callback.answer()
