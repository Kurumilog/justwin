# app/handlers/forms.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.services.userService import UserService
from app.services.formService import FormService
from app.services.taskService import TaskService
from app.states.form_states import FormStates
from app.keyboards import (
    get_form_management_keyboard,
    get_form_list_keyboard,
    get_form_actions_keyboard,
    get_form_confirm_delete_keyboard,
    get_form_task_selection_keyboard,
    get_back_to_cabinet_button
)

router = Router()


async def check_admin_rights(user_id: int) -> bool:
    """Проверка прав ADMIN или MANAGER"""
    access_level = await UserService.get_user_access_level(str(user_id))
    return access_level in [UserService.ACCESS_LEVEL_ADMIN, UserService.ACCESS_LEVEL_MANAGER]


@router.callback_query(F.data == "manage_forms")
async def show_form_management(callback: CallbackQuery, state: FSMContext) -> None:
    """Показать меню управления формами"""
    await state.clear()
    
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📄 <b>Управление формами</b>\n\n"
        "Формы содержат набор задач для проверок.\n"
        "Создавайте формы для разных объектов (цехов, участков и т.д.)",
        reply_markup=get_form_management_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "form_create")
async def form_create_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать создание формы"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    await state.set_state(FormStates.waiting_for_form_name)
    await callback.message.edit_text(
        "📝 <b>Создание формы</b>\n\n"
        "Введите название объекта (цеха, участка и т.д.):\n\n"
        "<i>Пример: Цех №1, Участок сборки, Склад материалов</i>",
        reply_markup=get_back_to_cabinet_button(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(FormStates.waiting_for_form_name, F.text)
async def form_create_process(message: Message, state: FSMContext) -> None:
    """Обработка создания формы"""
    part_name = message.text.strip()
    
    if len(part_name) < 3:
        await message.answer(
            "❌ Название слишком короткое. Минимум 3 символа.\n"
            "Попробуйте еще раз:"
        )
        return
    
    # Проверяем, существует ли уже форма с таким названием
    existing_forms = await FormService.get_all_forms()
    if any(form.get('part_name') == part_name for form in existing_forms):
        await message.answer(
            f"❌ <b>Форма с таким названием уже существует!</b>\n\n"
            f"Название: {part_name}\n\n"
            f"Пожалуйста, введите другое название:",
            parse_mode="HTML"
        )
        return
    
    # Создаем форму без задач
    try:
        form_id = await FormService.create_form(part_name, tasks=[])
    except Exception as e:
        await state.clear()
        await message.answer(
            f"❌ <b>Ошибка при создании формы</b>\n\n"
            f"Попробуйте еще раз или обратитесь к администратору.",
            reply_markup=get_form_management_keyboard(),
            parse_mode="HTML"
        )
        return
    
    await state.clear()
    
    # Сразу предлагаем добавить задачи
    tasks = await TaskService.get_all_tasks()
    
    if not tasks:
        await message.answer(
            f"✅ <b>Форма создана!</b>\n\n"
            f"Название: {part_name}\n"
            f"ID: {form_id}\n\n"
            f"⚠️ В системе пока нет задач. Создайте задачи, чтобы добавить их в форму.",
            reply_markup=get_form_actions_keyboard(form_id),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"✅ <b>Форма создана!</b>\n\n"
            f"Название: {part_name}\n"
            f"ID: {form_id}\n\n"
            f"Теперь добавьте задачи в форму:",
            reply_markup=get_form_task_selection_keyboard(tasks, [], form_id, 0),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "form_list")
async def form_list_show(callback: CallbackQuery, state: FSMContext) -> None:
    """Показать список форм"""
    await state.clear()
    
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    forms = await FormService.get_all_forms()
    
    if not forms:
        await callback.message.edit_text(
            "📋 <b>Список форм</b>\n\n"
            "Форм пока нет. Создайте первую форму!",
            reply_markup=get_form_management_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            f"📋 <b>Список форм</b> ({len(forms)} шт.)\n\n"
            "Выберите форму для просмотра:",
            reply_markup=get_form_list_keyboard(forms),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("form_view_"))
async def form_view(callback: CallbackQuery, state: FSMContext) -> None:
    """Просмотр конкретной формы"""
    await state.clear()
    
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    form_id = int(callback.data.split("_")[2])
    form = await FormService.get_form_by_id(form_id)
    
    if not form:
        await callback.answer("❌ Форма не найдена", show_alert=True)
        return
    
    # Получаем список задач формы
    tasks_str = form.get('tasks', '')
    task_ids = FormService.parse_tasks_string(tasks_str)
    
    # Формируем список задач для отображения
    task_list_text = ""
    if task_ids:
        all_tasks = await TaskService.get_all_tasks()
        tasks_dict = {t['id']: t for t in all_tasks}
        
        task_list_text = "\n\n<b>Задачи в форме:</b>\n"
        for i, task_id in enumerate(task_ids, 1):
            task = tasks_dict.get(task_id)
            if task:
                task_info = task.get('info', 'Нет описания')
                task_list_text += f"{i}. {task_info}\n"
        
        task_list_text += f"\n<i>Всего задач: {len(task_ids)}</i>"
    else:
        task_list_text = "\n\n⚠️ В форме пока нет задач"
    
    await callback.message.edit_text(
        f"📄 <b>Форма #{form_id}</b>\n\n"
        f"<b>Название:</b> {form.get('part_name', 'Без названия')}"
        f"{task_list_text}",
        reply_markup=get_form_actions_keyboard(form_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("form_edit_name_"))
async def form_edit_name_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать редактирование названия формы"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    form_id = int(callback.data.split("_")[3])
    form = await FormService.get_form_by_id(form_id)
    
    if not form:
        await callback.answer("❌ Форма не найдена", show_alert=True)
        return
    
    await state.set_state(FormStates.waiting_for_form_edit_name)
    await state.update_data(form_id=form_id)
    
    await callback.message.edit_text(
        f"✏️ <b>Редактирование формы #{form_id}</b>\n\n"
        f"Текущее название:\n{form.get('part_name', 'Нет')}\n\n"
        f"Введите новое название:",
        reply_markup=get_form_actions_keyboard(form_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(FormStates.waiting_for_form_edit_name, F.text)
async def form_edit_name_process(message: Message, state: FSMContext) -> None:
    """Обработка редактирования названия формы"""
    new_name = message.text.strip()
    
    if len(new_name) < 3:
        await message.answer(
            "❌ Название слишком короткое. Минимум 3 символа.\n"
            "Попробуйте еще раз:"
        )
        return
    
    data = await state.get_data()
    form_id = data.get('form_id')
    
    # Обновляем название
    success = await FormService.update_form_name(form_id, new_name)
    
    await state.clear()
    
    if success:
        await message.answer(
            f"✅ <b>Название формы #{form_id} обновлено!</b>\n\n"
            f"Новое название: {new_name}",
            reply_markup=get_form_actions_keyboard(form_id),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Ошибка при обновлении формы",
            reply_markup=get_form_management_keyboard()
        )


@router.callback_query(F.data.startswith("form_tasks_") & ~F.data.contains("save") & ~F.data.contains("toggle"))
async def form_tasks_show(callback: CallbackQuery, state: FSMContext) -> None:
    """Показать список задач для выбора (с пагинацией)"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    parts = callback.data.split("_")
    form_id = int(parts[2])
    page = int(parts[3]) if len(parts) > 3 else 0
    
    form = await FormService.get_form_by_id(form_id)
    if not form:
        await callback.answer("❌ Форма не найдена", show_alert=True)
        return
    
    # Получаем текущие задачи формы
    tasks_str = form.get('tasks', '')
    selected_task_ids = FormService.parse_tasks_string(tasks_str)
    
    # Сохраняем выбранные задачи в state
    await state.update_data(
        form_id=form_id,
        selected_tasks=selected_task_ids
    )
    
    # Получаем все задачи
    all_tasks = await TaskService.get_all_tasks()
    
    if not all_tasks:
        await callback.message.edit_text(
            "⚠️ В системе пока нет задач.\n"
            "Создайте задачи, чтобы добавить их в форму.",
            reply_markup=get_form_actions_keyboard(form_id)
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        f"📝 <b>Управление задачами формы</b>\n\n"
        f"<b>Форма:</b> {form.get('part_name')}\n\n"
        f"Нажмите на задачу, чтобы добавить/убрать её из формы:",
        reply_markup=get_form_task_selection_keyboard(all_tasks, selected_task_ids, form_id, page),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("form_task_toggle_"))
async def form_task_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    """Переключить задачу (добавить/убрать из формы)"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    parts = callback.data.split("_")
    form_id = int(parts[3])
    task_id = int(parts[4])
    page = int(parts[5]) if len(parts) > 5 else 0
    
    # Получаем текущие выбранные задачи из state
    data = await state.get_data()
    selected_tasks = data.get('selected_tasks', [])
    
    # Переключаем задачу
    if task_id in selected_tasks:
        selected_tasks.remove(task_id)
        action_text = "убрана из"
    else:
        selected_tasks.append(task_id)
        action_text = "добавлена в"
    
    # Обновляем state
    await state.update_data(selected_tasks=selected_tasks)
    
    # Получаем все задачи и форму
    all_tasks = await TaskService.get_all_tasks()
    form = await FormService.get_form_by_id(form_id)
    
    # Обновляем клавиатуру
    await callback.message.edit_text(
        f"📝 <b>Управление задачами формы</b>\n\n"
        f"<b>Форма:</b> {form.get('part_name')}\n\n"
        f"Нажмите на задачу, чтобы добавить/убрать её из формы:",
        reply_markup=get_form_task_selection_keyboard(all_tasks, selected_tasks, form_id, page),
        parse_mode="HTML"
    )
    
    # Показываем уведомление
    task = next((t for t in all_tasks if t['id'] == task_id), None)
    if task:
        task_name = task.get('info', '')[:30]
        await callback.answer(f"Задача {action_text} форму")


@router.callback_query(F.data.startswith("form_tasks_save_"))
async def form_tasks_save(callback: CallbackQuery, state: FSMContext) -> None:
    """Сохранить выбранные задачи для формы"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    form_id = int(callback.data.split("_")[3])
    
    # Получаем выбранные задачи из state
    data = await state.get_data()
    selected_tasks = data.get('selected_tasks', [])
    
    # Сохраняем в базу
    success = await FormService.update_form_tasks(form_id, selected_tasks)
    
    await state.clear()
    
    if success:
        form = await FormService.get_form_by_id(form_id)
        await callback.message.edit_text(
            f"✅ <b>Задачи формы обновлены!</b>\n\n"
            f"<b>Форма:</b> {form.get('part_name')}\n"
            f"<b>Количество задач:</b> {len(selected_tasks)}",
            reply_markup=get_form_actions_keyboard(form_id),
            parse_mode="HTML"
        )
        await callback.answer("Сохранено!", show_alert=False)
    else:
        await callback.answer("❌ Ошибка при сохранении", show_alert=True)


@router.callback_query(F.data.startswith("form_delete_") & ~F.data.contains("confirm"))
async def form_delete_ask(callback: CallbackQuery) -> None:
    """Запросить подтверждение удаления"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    form_id = int(callback.data.split("_")[2])
    form = await FormService.get_form_by_id(form_id)
    
    if not form:
        await callback.answer("❌ Форма не найдена", show_alert=True)
        return
    
    tasks_str = form.get('tasks', '')
    task_ids = FormService.parse_tasks_string(tasks_str)
    
    await callback.message.edit_text(
        f"⚠️ <b>Удаление формы #{form_id}</b>\n\n"
        f"<b>Название:</b> {form.get('part_name', 'Без названия')}\n"
        f"<b>Задач в форме:</b> {len(task_ids)}\n\n"
        f"Вы уверены, что хотите удалить эту форму?\n"
        f"<i>Это действие нельзя отменить!</i>",
        reply_markup=get_form_confirm_delete_keyboard(form_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("form_delete_confirm_"))
async def form_delete_confirm(callback: CallbackQuery) -> None:
    """Подтверждение удаления формы"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    form_id = int(callback.data.split("_")[3])
    
    success = await FormService.delete_form(form_id)
    
    if success:
        await callback.message.edit_text(
            f"✅ Форма #{form_id} успешно удалена!",
            reply_markup=get_form_management_keyboard()
        )
        await callback.answer("Форма удалена", show_alert=False)
    else:
        await callback.answer("❌ Ошибка при удалении формы", show_alert=True)


@router.callback_query(F.data == "form_search")
async def form_search_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать поиск формы"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    await state.set_state(FormStates.waiting_for_search_query)
    await callback.message.edit_text(
        "🔍 <b>Поиск формы</b>\n\n"
        "Введите поисковый запрос (название объекта):",
        reply_markup=get_form_management_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(FormStates.waiting_for_search_query, F.text)
async def form_search_process(message: Message, state: FSMContext) -> None:
    """Обработка поиска формы"""
    query = message.text.strip().lower()
    
    forms = await FormService.get_all_forms()
    filtered_forms = [f for f in forms if query in f.get('part_name', '').lower()]
    
    await state.clear()
    
    if not filtered_forms:
        await message.answer(
            f"🔍 По запросу «{query}» ничего не найдено",
            reply_markup=get_form_management_keyboard()
        )
    else:
        await message.answer(
            f"🔍 Найдено форм: {len(filtered_forms)}\n\n"
            f"Выберите форму:",
            reply_markup=get_form_list_keyboard(filtered_forms)
        )


# Обработчики для информационных кнопок
@router.callback_query(F.data == "page_info")
async def page_info_handler(callback: CallbackQuery) -> None:
    """Обработка нажатия на информацию о странице"""
    await callback.answer("Используйте стрелки для навигации", show_alert=False)


@router.callback_query(F.data == "selected_info")
async def selected_info_handler(callback: CallbackQuery) -> None:
    """Обработка нажатия на информацию о выбранных задачах"""
    await callback.answer("Количество выбранных задач", show_alert=False)
