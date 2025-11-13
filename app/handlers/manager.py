# app/handlers/manager.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from app.services.userService import UserService
from app.services.formService import FormService
from app.services.plannedCheckService import PlannedCheckService
from app.keyboards.manager_keyboards import (
    get_manager_cabinet_keyboard,
    get_brigades_list_keyboard,
    get_date_selection_keyboard,
    get_reviewers_list_keyboard,
    get_confirm_planned_check_keyboard
)
from app.states.manager_states import ManagerStates

router = Router()


async def check_manager_rights(callback: CallbackQuery) -> bool:
    """Проверить, является ли пользователь менеджером или админом"""
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    if not user or user.get('access_level') not in ['manager', 'admin']:
        await callback.answer("⛔ У вас нет доступа к этому разделу", show_alert=True)
        return False
    return True


@router.callback_query(F.data == "checks_management")
async def show_checks_management(callback: CallbackQuery):
    """Показать меню управления проверками"""
    if not await check_manager_rights(callback):
        return
    
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    username = user.get('name', 'Пользователь')
    
    # Получаем количество запланированных проверок
    upcoming_checks = await PlannedCheckService.get_upcoming_checks(limit=100)
    checks_count = len(upcoming_checks)
    
    text = (
        f"📊 <b>Управление проверками</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 {username}\n\n"
        f"📋 Запланировано проверок: <b>{checks_count}</b>\n\n"
        f"Выберите действие:"
    )
    
    from app.keyboards.manager_keyboards import get_planned_checks_keyboard
    
    await callback.message.edit_text(
        text,
        reply_markup=get_planned_checks_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "manager_cabinet")
async def show_manager_cabinet(callback: CallbackQuery):
    """Показать личный кабинет менеджера"""
    if not await check_manager_rights(callback):
        return
    
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    username = user.get('name', 'Менеджер')
    
    text = (
        f"👨‍💼 <b>Личный кабинет менеджера</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 {username}\n"
        f"🔑 Роль: <code>Менеджер</code>\n\n"
        f"📋 Доступные функции:\n"
        f"• Управление формами и задачами\n"
        f"• Планирование проверок бригад\n"
        f"• Просмотр отчётов\n"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_manager_cabinet_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "manager_plan_checks")
async def plan_checks_start(callback: CallbackQuery, state: FSMContext):
    """Начать планирование проверки - показать список бригад"""
    if not await check_manager_rights(callback):
        return
    
    # Очищаем состояние
    await state.clear()
    
    # Получить все формы (бригады)
    forms = await FormService.get_all_forms()
    
    if not forms:
        from app.keyboards.manager_keyboards import get_planned_checks_keyboard
        await callback.message.edit_text(
            "⚠️ <b>Нет доступных бригад</b>\n\n"
            "Сначала создайте формы в разделе\n"
            "<b>🏢 Рабочий кабинет → Управление формами</b>.",
            reply_markup=get_planned_checks_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("⚠️ Создайте формы для планирования проверок", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📅 <b>Планирование проверки</b>\n\n"
        "Выберите бригаду для проверки:",
        reply_markup=get_brigades_list_keyboard(forms),
        parse_mode="HTML"
    )
    await state.set_state(ManagerStates.planning_check_select_brigade)
    await callback.answer()


@router.callback_query(F.data.startswith("plan_check_brigade_"), ManagerStates.planning_check_select_brigade)
async def plan_checks_select_brigade(callback: CallbackQuery, state: FSMContext):
    """Выбрана бригада, выбираем дату"""
    if not await check_manager_rights(callback):
        return
    
    form_id = int(callback.data.split("_")[-1])
    form = await FormService.get_form_by_id(form_id)
    
    if not form:
        await callback.answer("❌ Форма не найдена", show_alert=True)
        return
    
    # Сохранить выбранную форму
    await state.update_data(form_id=form_id, part_name=form.get('part_name'))
    
    await callback.message.edit_text(
        f"📅 <b>Планирование проверки</b>\n\n"
        f"🏭 Бригада: <b>{form.get('part_name')}</b>\n\n"
        f"Выберите дату проверки:",
        reply_markup=get_date_selection_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ManagerStates.planning_check_select_date)
    await callback.answer()


@router.callback_query(F.data == "plan_check_date_tomorrow", ManagerStates.planning_check_select_date)
async def plan_checks_date_tomorrow(callback: CallbackQuery, state: FSMContext):
    """Выбрана дата - завтра"""
    if not await check_manager_rights(callback):
        return
    
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime('%Y-%m-%d')
    
    await state.update_data(date=date_str)
    
    data = await state.get_data()
    part_name = data.get('part_name', 'Неизвестно')
    
    await callback.message.edit_text(
        f"🕐 <b>Планирование проверки</b>\n\n"
        f"🏭 Бригада: <b>{part_name}</b>\n"
        f"📅 Дата: <b>{date_str}</b>\n\n"
        f"Введите время проверки в формате <code>ЧЧ:ММ</code>\n"
        f"Например: <code>10:00</code> или <code>14:30</code>",
        parse_mode="HTML"
    )
    await state.set_state(ManagerStates.planning_check_select_time)
    await callback.answer()


@router.callback_query(F.data == "plan_check_date_custom", ManagerStates.planning_check_select_date)
async def plan_checks_date_custom(callback: CallbackQuery, state: FSMContext):
    """Выбрана дата - пользовательская"""
    if not await check_manager_rights(callback):
        return
    
    data = await state.get_data()
    part_name = data.get('part_name', 'Неизвестно')
    
    await callback.message.edit_text(
        f"📅 <b>Планирование проверки</b>\n\n"
        f"🏭 Бригада: <b>{part_name}</b>\n\n"
        f"Введите дату в формате <code>ГГГГ-ММ-ДД</code>\n"
        f"Например: <code>2025-11-15</code>",
        parse_mode="HTML"
    )
    await state.set_state(ManagerStates.planning_check_select_time)
    await callback.answer()


@router.message(ManagerStates.planning_check_select_time)
async def plan_checks_time_entered(message: Message, state: FSMContext):
    """Введено время или дата+время"""
    data = await state.get_data()
    
    # Проверяем, есть ли уже дата
    if 'date' in data:
        # Уже есть дата, введено время
        time_str = message.text.strip()
        
        # Проверка формата времени
        try:
            time_obj = datetime.strptime(time_str, '%H:%M')
            date_str = data['date']
        except ValueError:
            await message.answer(
                "❌ Неверный формат времени!\n\n"
                "Введите время в формате <code>ЧЧ:ММ</code>, например: <code>10:00</code>",
                parse_mode="HTML"
            )
            return
    else:
        # Дата не введена, пытаемся распарсить дату
        date_str = message.text.strip()
        
        # Проверка формата даты
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_str = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            await message.answer(
                "❌ Неверный формат даты!\n\n"
                "Введите дату в формате <code>ГГГГ-ММ-ДД</code>, например: <code>2025-11-15</code>",
                parse_mode="HTML"
            )
            return
        
        # Сохраняем дату и просим ввести время
        await state.update_data(date=date_str)
        
        part_name = data.get('part_name', 'Неизвестно')
        await message.answer(
            f"🕐 <b>Планирование проверки</b>\n\n"
            f"🏭 Бригада: <b>{part_name}</b>\n"
            f"📅 Дата: <b>{date_str}</b>\n\n"
            f"Введите время проверки в формате <code>ЧЧ:ММ</code>\n"
            f"Например: <code>10:00</code> или <code>14:30</code>",
            parse_mode="HTML"
        )
        return
    
    # Собираем полную дату и время
    full_datetime_str = f"{date_str} {time_str}:00"
    await state.update_data(datetime=full_datetime_str)
    
    # Получаем список проверяющих (office_worker)
    reviewers = await UserService.get_office_workers()
    
    if not reviewers:
        await message.answer(
            "⚠️ <b>Нет доступных проверяющих</b>\n\n"
            "В системе нет пользователей с ролью <code>office_worker</code>.",
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    part_name = data.get('part_name', 'Неизвестно')
    
    await message.answer(
        f"👤 <b>Планирование проверки</b>\n\n"
        f"🏭 Бригада: <b>{part_name}</b>\n"
        f"📅 Дата и время: <b>{date_str} {time_str}</b>\n\n"
        f"Выберите проверяющего:",
        reply_markup=get_reviewers_list_keyboard(reviewers),
        parse_mode="HTML"
    )
    await state.set_state(ManagerStates.planning_check_select_reviewer)


@router.callback_query(F.data.startswith("plan_check_reviewer_"), ManagerStates.planning_check_select_reviewer)
async def plan_checks_select_reviewer(callback: CallbackQuery, state: FSMContext):
    """Выбран проверяющий"""
    if not await check_manager_rights(callback):
        return
    
    # Извлекаем reviewer_id и name из callback_data
    # Формат: plan_check_reviewer_{user_id}_{name}
    callback_parts = callback.data.replace("plan_check_reviewer_", "")
    parts = callback_parts.split("_", 1)
    
    if len(parts) >= 1:
        reviewer_id = parts[0]
        reviewer_name = parts[1] if len(parts) > 1 else "Неизвестно"
    else:
        await callback.answer("❌ Ошибка в данных", show_alert=True)
        return
    
    await state.update_data(reviewer_id=reviewer_id, reviewer_name=reviewer_name)
    
    data = await state.get_data()
    part_name = data.get('part_name', 'Неизвестно')
    datetime_str = data.get('datetime', 'Неизвестно')
    
    await callback.message.edit_text(
        f"✅ <b>Подтверждение планирования проверки</b>\n\n"
        f"🏭 Бригада: <b>{part_name}</b>\n"
        f"📅 Дата и время: <b>{datetime_str}</b>\n"
        f"👤 Проверяющий: <b>{reviewer_name}</b>\n\n"
        f"Подтвердите создание запланированной проверки:",
        reply_markup=get_confirm_planned_check_keyboard(data.get('form_id')),
        parse_mode="HTML"
    )
    await state.set_state(ManagerStates.planning_check_confirm)
    await callback.answer()


@router.callback_query(F.data.startswith("plan_check_confirm_"), ManagerStates.planning_check_confirm)
async def plan_checks_confirm(callback: CallbackQuery, state: FSMContext):
    """Подтверждение создания проверки"""
    if not await check_manager_rights(callback):
        return
    
    data = await state.get_data()
    form_id = data.get('form_id')
    datetime_str = data.get('datetime')
    reviewer_id = data.get('reviewer_id')
    
    if not all([form_id, datetime_str, reviewer_id]):
        await callback.answer("❌ Ошибка: не хватает данных", show_alert=True)
        await state.clear()
        return
    
    # Создаем запланированную проверку
    try:
        check_id = await PlannedCheckService.create_planned_check(
            time=datetime_str,
            form_id=form_id,
            reviewer_id=reviewer_id
        )
        
        from app.keyboards.manager_keyboards import get_planned_checks_keyboard
        await callback.message.edit_text(
            f"✅ <b>Проверка успешно запланирована!</b>\n\n"
            f"🏭 Бригада: <b>{data.get('part_name')}</b>\n"
            f"📅 Дата и время: <b>{datetime_str}</b>\n"
            f"👤 Проверяющий: <b>{data.get('reviewer_name')}</b>\n\n"
            f"ID проверки: <code>{check_id}</code>",
            reply_markup=get_planned_checks_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("✅ Проверка запланирована!")
        
    except Exception as e:
        from app.keyboards.manager_keyboards import get_planned_checks_keyboard
        await callback.message.edit_text(
            f"❌ <b>Ошибка при создании проверки:</b>\n\n"
            f"<code>{str(e)}</code>",
            reply_markup=get_planned_checks_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("❌ Ошибка при создании проверки", show_alert=True)
    
    await state.clear()


@router.callback_query(F.data == "manager_view_planned_checks")
async def view_planned_checks(callback: CallbackQuery):
    """Просмотр запланированных проверок"""
    if not await check_manager_rights(callback):
        return
    
    checks = await PlannedCheckService.get_upcoming_checks(limit=20)
    
    if not checks:
        from app.keyboards.manager_keyboards import get_planned_checks_keyboard
        await callback.message.edit_text(
            "📋 <b>Запланированные проверки</b>\n\n"
            "⚠️ Нет запланированных проверок.",
            reply_markup=get_planned_checks_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    text = "📋 <b>Запланированные проверки</b>\n\n"
    
    for check in checks:
        check_id = check.get('id')
        time_str = check.get('time')
        form_id = check.get('form_id')
        reviewer_id = check.get('reviewer_id')
        
        # Получаем данные формы и проверяющего
        form = await FormService.get_form_by_id(form_id)
        reviewer = await UserService.get_user_by_id(reviewer_id)
        
        part_name = form.get('part_name', 'Неизвестно') if form else 'Неизвестно'
        reviewer_name = reviewer.get('name', 'Неизвестно') if reviewer else 'Неизвестно'
        
        text += (
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"ID: <code>{check_id}</code>\n"
            f"🏭 Бригада: <b>{part_name}</b>\n"
            f"📅 Время: <b>{time_str}</b>\n"
            f"👤 Проверяющий: <b>{reviewer_name}</b>\n\n"
        )
    
    from app.keyboards.manager_keyboards import get_planned_checks_keyboard
    await callback.message.edit_text(
        text,
        reply_markup=get_planned_checks_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
