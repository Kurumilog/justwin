# app/handlers/tasks.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.services.userService import UserService
from app.services.taskService import TaskService
from app.states.task_states import TaskStates
from app.keyboards import (
    get_task_management_keyboard,
    get_task_list_keyboard,
    get_task_actions_keyboard,
    get_task_confirm_delete_keyboard,
    get_back_to_cabinet_button
)

router = Router()


async def check_admin_rights(user_id: int) -> bool:
    """Проверка прав ADMIN или MANAGER"""
    access_level = await UserService.get_user_access_level(str(user_id))
    return access_level in [UserService.ACCESS_LEVEL_ADMIN, UserService.ACCESS_LEVEL_MANAGER]


@router.callback_query(F.data == "manage_tasks")
async def show_task_management(callback: CallbackQuery, state: FSMContext) -> None:
    """Показать меню управления задачами"""
    await state.clear()
    
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📝 <b>Управление задачами</b>\n\n"
        "Здесь вы можете создавать и редактировать задачи,\n"
        "которые будут использоваться в формах проверок.",
        reply_markup=get_task_management_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "task_create")
async def task_create_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать создание задачи"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    await state.set_state(TaskStates.waiting_for_task_info)
    await callback.message.edit_text(
        "📝 <b>Создание задачи</b>\n\n"
        "Введите описание задачи:\n\n"
        "<i>Пример: Проверить наличие аптечки на рабочем месте</i>",
        reply_markup=get_back_to_cabinet_button(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(TaskStates.waiting_for_task_info, F.text)
async def task_create_process(message: Message, state: FSMContext) -> None:
    """Обработка создания задачи"""
    task_info = message.text.strip()
    
    if len(task_info) < 5:
        await message.answer(
            "❌ Описание задачи слишком короткое. Минимум 5 символов.\n"
            "Попробуйте еще раз:"
        )
        return
    
    # Создаем задачу
    task_id = await TaskService.create_task(task_info)
    
    await state.clear()
    await message.answer(
        f"✅ <b>Задача создана!</b>\n\n"
        f"ID: {task_id}\n"
        f"Описание: {task_info}",
        reply_markup=get_task_management_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "task_list")
async def task_list_show(callback: CallbackQuery, state: FSMContext) -> None:
    """Показать список задач"""
    await state.clear()
    
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    tasks = await TaskService.get_all_tasks()
    
    if not tasks:
        await callback.message.edit_text(
            "📋 <b>Список задач</b>\n\n"
            "Задач пока нет. Создайте первую задачу!",
            reply_markup=get_task_management_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            f"📋 <b>Список задач</b> ({len(tasks)} шт.)\n\n"
            "Выберите задачу для просмотра:",
            reply_markup=get_task_list_keyboard(tasks),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("task_view_"))
async def task_view(callback: CallbackQuery, state: FSMContext) -> None:
    """Просмотр конкретной задачи"""
    await state.clear()
    
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    task_id = int(callback.data.split("_")[2])
    task = await TaskService.get_task_by_id(task_id)
    
    if not task:
        await callback.answer("❌ Задача не найдена", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"📌 <b>Задача #{task_id}</b>\n\n"
        f"{task.get('info', 'Без описания')}",
        reply_markup=get_task_actions_keyboard(task_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task_edit_"))
async def task_edit_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать редактирование задачи"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    task_id = int(callback.data.split("_")[2])
    task = await TaskService.get_task_by_id(task_id)
    
    if not task:
        await callback.answer("❌ Задача не найдена", show_alert=True)
        return
    
    await state.set_state(TaskStates.waiting_for_task_edit)
    await state.update_data(task_id=task_id)
    
    await callback.message.edit_text(
        f"✏️ <b>Редактирование задачи #{task_id}</b>\n\n"
        f"Текущее описание:\n{task.get('info', 'Нет')}\n\n"
        f"Введите новое описание:",
        reply_markup=get_task_actions_keyboard(task_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(TaskStates.waiting_for_task_edit, F.text)
async def task_edit_process(message: Message, state: FSMContext) -> None:
    """Обработка редактирования задачи"""
    new_info = message.text.strip()
    
    if len(new_info) < 5:
        await message.answer(
            "❌ Описание задачи слишком короткое. Минимум 5 символов.\n"
            "Попробуйте еще раз:"
        )
        return
    
    data = await state.get_data()
    task_id = data.get('task_id')
    
    # Обновляем задачу
    success = await TaskService.update_task(task_id, new_info)
    
    await state.clear()
    
    if success:
        await message.answer(
            f"✅ <b>Задача #{task_id} обновлена!</b>\n\n"
            f"Новое описание: {new_info}",
            reply_markup=get_task_actions_keyboard(task_id),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Ошибка при обновлении задачи",
            reply_markup=get_task_management_keyboard()
        )


@router.callback_query(F.data.startswith("task_delete_") & ~F.data.contains("confirm"))
async def task_delete_ask(callback: CallbackQuery) -> None:
    """Запросить подтверждение удаления"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    task_id = int(callback.data.split("_")[2])
    task = await TaskService.get_task_by_id(task_id)
    
    if not task:
        await callback.answer("❌ Задача не найдена", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"⚠️ <b>Удаление задачи #{task_id}</b>\n\n"
        f"{task.get('info', 'Без описания')}\n\n"
        f"Вы уверены, что хотите удалить эту задачу?\n"
        f"<i>Это действие нельзя отменить!</i>",
        reply_markup=get_task_confirm_delete_keyboard(task_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task_delete_confirm_"))
async def task_delete_confirm(callback: CallbackQuery) -> None:
    """Подтверждение удаления задачи"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    task_id = int(callback.data.split("_")[3])
    
    success = await TaskService.delete_task(task_id)
    
    if success:
        await callback.message.edit_text(
            f"✅ Задача #{task_id} успешно удалена!",
            reply_markup=get_task_management_keyboard()
        )
        await callback.answer("Задача удалена", show_alert=False)
    else:
        await callback.answer("❌ Ошибка при удалении задачи", show_alert=True)


@router.callback_query(F.data == "task_search")
async def task_search_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать поиск задачи"""
    if not await check_admin_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    await state.set_state(TaskStates.waiting_for_search_query)
    await callback.message.edit_text(
        "🔍 <b>Поиск задачи</b>\n\n"
        "Введите поисковый запрос:",
        reply_markup=get_task_management_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(TaskStates.waiting_for_search_query, F.text)
async def task_search_process(message: Message, state: FSMContext) -> None:
    """Обработка поиска задачи"""
    query = message.text.strip()
    
    # TODO: Реализовать поиск в TaskService
    tasks = await TaskService.get_all_tasks()
    filtered_tasks = [t for t in tasks if query.lower() in t.get('info', '').lower()]
    
    await state.clear()
    
    if not filtered_tasks:
        await message.answer(
            f"🔍 По запросу «{query}» ничего не найдено",
            reply_markup=get_task_management_keyboard()
        )
    else:
        await message.answer(
            f"🔍 Найдено задач: {len(filtered_tasks)}\n\n"
            f"Выберите задачу:",
            reply_markup=get_task_list_keyboard(filtered_tasks)
        )
