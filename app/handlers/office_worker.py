# app/handlers/office_worker.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.services.userService import UserService
from app.services.formService import FormService
from app.services.taskService import TaskService
from app.services.checkService import CheckService
from app.services.errorService import ErrorService
from app.keyboards.office_worker_keyboards import (
    get_task_check_keyboard,
    get_check_complete_keyboard,
    get_error_options_keyboard,
    get_error_confirm_keyboard
)
from app.states.office_worker_states import CheckStates

router = Router()


async def check_office_worker_rights(callback: CallbackQuery) -> bool:
    """Проверить, является ли пользователь офисным работником"""
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    if not user or user.get('access_level') != UserService.ACCESS_LEVEL_OFFICE_WORKER:
        await callback.answer("⛔ У вас нет доступа к этому разделу", show_alert=True)
        return False
    return True


@router.callback_query(F.data == "conduct_check")
async def start_check(callback: CallbackQuery, state: FSMContext):
    """Начать проверку - показать задачи блока office_worker"""
    if not await check_office_worker_rights(callback):
        return
    
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    part_name = user.get('part_name')
    
    if not part_name:
        await callback.answer(
            "⚠️ У вас не назначен блок для проверки. Обратитесь к администратору.",
            show_alert=True
        )
        return
    
    # Получаем форму по part_name (блок)
    form = await FormService.get_form_by_part_name(part_name)
    
    if not form:
        await callback.answer(
            f"⚠️ Форма для блока '{part_name}' не найдена. Обратитесь к администратору.",
            show_alert=True
        )
        return
    
    # Получаем задачи формы
    tasks_str = form.get('tasks', '')
    task_ids = FormService.parse_tasks_string(tasks_str)
    
    if not task_ids:
        await callback.answer(
            "⚠️ В форме нет задач для проверки.",
            show_alert=True
        )
        return
    
    # Получаем информацию о задачах
    tasks = []
    for task_id in task_ids:
        task = await TaskService.get_task_by_id(task_id)
        if task:
            tasks.append(task)
    
    if not tasks:
        await callback.answer(
            "⚠️ Задачи не найдены в системе.",
            show_alert=True
        )
        return
    
    # Сохраняем данные в state
    await state.update_data(
        form_id=form.get('id'),
        part_name=part_name,
        task_ids=task_ids,
        current_task_index=0,
        grades=[],  # Список оценок: 1 = ОК, 0 = Не ОК
        errors_ids=[]  # Список ID ошибок
    )
    await state.set_state(CheckStates.checking_tasks)
    
    # Показываем первую задачу
    await show_task_for_check(callback, state)


async def show_task_for_check(callback: CallbackQuery, state: FSMContext):
    """Показать задачу для проверки"""
    data = await state.get_data()
    task_ids = data.get('task_ids', [])
    current_index = data.get('current_task_index', 0)
    grades = data.get('grades', [])
    
    if current_index >= len(task_ids):
        # Все задачи проверены, завершаем проверку
        await complete_check(callback, state)
        return
    
    task_id = task_ids[current_index]
    task = await TaskService.get_task_by_id(task_id)
    
    if not task:
        await callback.answer("⚠️ Задача не найдена", show_alert=True)
        return
    
    task_info = task.get('info', 'Без описания')
    part_name = data.get('part_name', 'Блок')
    total_tasks = len(task_ids)
    task_num = current_index + 1
    
    text = (
        f"✅ <b>Проверка блока: {part_name}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Задача {task_num} из {total_tasks}\n\n"
        f"<b>{task_info}</b>\n\n"
        f"Выберите результат проверки:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_task_check_keyboard(task_id, task_num, total_tasks),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task_check_ok_"))
async def task_check_ok(callback: CallbackQuery, state: FSMContext):
    """Задача выполнена (ОК)"""
    if not await check_office_worker_rights(callback):
        return
    
    # Извлекаем task_id из callback_data
    parts = callback.data.split("_")
    task_id = int(parts[3])
    
    data = await state.get_data()
    task_ids = data.get('task_ids', [])
    current_index = data.get('current_task_index', 0)
    grades = data.get('grades', [])
    
    # Проверяем, что это правильная задача
    if current_index < len(task_ids) and task_ids[current_index] == task_id:
        # Добавляем оценку 1 (ОК)
        grades.append(1)
        await state.update_data(grades=grades, current_task_index=current_index + 1)
        
        # Переходим к следующей задаче
        await show_task_for_check(callback, state)
    else:
        await callback.answer("⚠️ Ошибка: неверная задача", show_alert=True)


@router.callback_query(F.data.startswith("task_check_fail_"))
async def task_check_fail(callback: CallbackQuery, state: FSMContext):
    """Задача не выполнена (Не ОК) - предлагаем добавить ошибку"""
    if not await check_office_worker_rights(callback):
        return
    
    # Извлекаем task_id из callback_data
    parts = callback.data.split("_")
    task_id = int(parts[3])
    
    data = await state.get_data()
    task_ids = data.get('task_ids', [])
    current_index = data.get('current_task_index', 0)
    
    # Проверяем, что это правильная задача
    if current_index < len(task_ids) and task_ids[current_index] == task_id:
        task = await TaskService.get_task_by_id(task_id)
        task_info = task.get('info', 'Без описания') if task else 'Задача'
        
        # Сохраняем текущий task_id для добавления ошибки
        await state.update_data(
            current_error_task_id=task_id,
            current_error_comment=None,
            current_error_photo=None
        )
        
        text = (
            f"❌ <b>Задача не выполнена</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 <b>{task_info}</b>\n\n"
            f"Вы можете добавить комментарий и/или фото к ошибке, или продолжить без деталей."
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_error_options_keyboard(task_id),
            parse_mode="HTML"
        )
        await callback.answer()
    else:
        await callback.answer("⚠️ Ошибка: неверная задача", show_alert=True)


@router.callback_query(F.data.startswith("error_add_comment_"))
async def error_add_comment_start(callback: CallbackQuery, state: FSMContext):
    """Начать добавление комментария к ошибке"""
    if not await check_office_worker_rights(callback):
        return
    
    parts = callback.data.split("_")
    task_id = int(parts[3])
    
    await state.set_state(CheckStates.adding_error_comment)
    await state.update_data(current_error_task_id=task_id)
    
    await callback.message.edit_text(
        "📝 <b>Добавление комментария к ошибке</b>\n\n"
        "Введите комментарий к ошибке:",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(CheckStates.adding_error_comment, F.text)
async def error_comment_received(message: Message, state: FSMContext):
    """Обработка полученного комментария"""
    # Проверяем права пользователя
    user = await UserService.get_user_by_id(str(message.from_user.id))
    if not user or user.get('access_level') != UserService.ACCESS_LEVEL_OFFICE_WORKER:
        await message.answer("⛔ У вас нет доступа к этому разделу")
        await state.clear()
        return
    
    comment = message.text.strip()
    
    if len(comment) < 3:
        await message.answer(
            "❌ Комментарий слишком короткий. Минимум 3 символа.\n"
            "Попробуйте еще раз:"
        )
        return
    
    data = await state.get_data()
    task_id = data.get('current_error_task_id')
    current_photo = data.get('current_error_photo')
    
    await state.update_data(current_error_comment=comment)
    
    # Показываем подтверждение
    text = (
        f"📝 <b>Комментарий добавлен</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Комментарий:</b> {comment}\n"
    )
    
    if current_photo:
        text += f"\n📷 Фото: добавлено"
    else:
        text += f"\n📷 Фото: не добавлено"
    
    text += "\n\nВы можете добавить фото или сохранить ошибку."
    
    await message.answer(
        text,
        reply_markup=get_error_confirm_keyboard(task_id),
        parse_mode="HTML"
    )
    await state.set_state(CheckStates.checking_tasks)


@router.callback_query(F.data.startswith("error_add_photo_"))
async def error_add_photo_start(callback: CallbackQuery, state: FSMContext):
    """Начать добавление фото к ошибке"""
    if not await check_office_worker_rights(callback):
        return
    
    parts = callback.data.split("_")
    task_id = int(parts[3])
    
    await state.set_state(CheckStates.adding_error_photo)
    await state.update_data(current_error_task_id=task_id)
    
    await callback.message.edit_text(
        "📷 <b>Добавление фото к ошибке</b>\n\n"
        "Отправьте фото:",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(CheckStates.adding_error_photo, F.photo)
async def error_photo_received(message: Message, state: FSMContext):
    """Обработка полученного фото"""
    # Проверяем права пользователя
    user = await UserService.get_user_by_id(str(message.from_user.id))
    if not user or user.get('access_level') != UserService.ACCESS_LEVEL_OFFICE_WORKER:
        await message.answer("⛔ У вас нет доступа к этому разделу")
        await state.clear()
        return
    
    # Получаем file_id самого большого фото
    photo = message.photo[-1]
    photo_file_id = photo.file_id
    
    data = await state.get_data()
    task_id = data.get('current_error_task_id')
    current_comment = data.get('current_error_comment')
    
    await state.update_data(current_error_photo=photo_file_id)
    
    # Показываем подтверждение
    text = (
        f"📷 <b>Фото добавлено</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    if current_comment:
        text += f"📝 <b>Комментарий:</b> {current_comment}\n"
    else:
        text += f"📝 Комментарий: не добавлен\n"
    
    text += f"📷 Фото: добавлено\n\n"
    text += "Вы можете добавить комментарий или сохранить ошибку."
    
    await message.answer_photo(
        photo=photo_file_id,
        caption=text,
        reply_markup=get_error_confirm_keyboard(task_id),
        parse_mode="HTML"
    )
    await state.set_state(CheckStates.checking_tasks)


@router.callback_query(F.data.startswith("error_skip_"))
async def error_skip(callback: CallbackQuery, state: FSMContext):
    """Пропустить добавление ошибки и продолжить"""
    if not await check_office_worker_rights(callback):
        return
    
    parts = callback.data.split("_")
    task_id = int(parts[2])
    
    data = await state.get_data()
    task_ids = data.get('task_ids', [])
    current_index = data.get('current_task_index', 0)
    grades = data.get('grades', [])
    
    # Проверяем, что это правильная задача
    if current_index < len(task_ids) and task_ids[current_index] == task_id:
        # Добавляем оценку 0 (Не ОК) без ошибки
        grades.append(0)
        await state.update_data(
            grades=grades,
            current_task_index=current_index + 1,
            current_error_task_id=None,
            current_error_comment=None,
            current_error_photo=None
        )
        
        # Переходим к следующей задаче
        await show_task_for_check(callback, state)
    else:
        await callback.answer("⚠️ Ошибка: неверная задача", show_alert=True)


@router.callback_query(F.data.startswith("error_save_"))
async def error_save(callback: CallbackQuery, state: FSMContext):
    """Сохранить ошибку и продолжить"""
    if not await check_office_worker_rights(callback):
        return
    
    parts = callback.data.split("_")
    task_id = int(parts[2])
    
    data = await state.get_data()
    task_ids = data.get('task_ids', [])
    current_index = data.get('current_task_index', 0)
    grades = data.get('grades', [])
    errors_ids = data.get('errors_ids', [])
    
    # Проверяем, что это правильная задача
    if current_index < len(task_ids) and task_ids[current_index] == task_id:
        comment = data.get('current_error_comment')
        photo_url = data.get('current_error_photo')
        
        # Убеждаемся, что комментарий не None (база данных требует NOT NULL)
        if not comment or comment is None:
            comment = 'Ошибка без комментария'
        
        # Сохраняем ошибку
        try:
            error_id = await ErrorService.create_error(
                comment=comment,
                photo_url=photo_url
            )
            
            # Добавляем ID ошибки в список
            errors_ids.append(error_id)
            
            # Добавляем оценку 0 (Не ОК)
            grades.append(0)
            
            await state.update_data(
                grades=grades,
                errors_ids=errors_ids,
                current_task_index=current_index + 1,
                current_error_task_id=None,
                current_error_comment=None,
                current_error_photo=None
            )
            
            await callback.answer("✅ Ошибка сохранена", show_alert=False)
            
            # Переходим к следующей задаче
            await show_task_for_check(callback, state)
            
        except Exception as e:
            await callback.answer(
                f"❌ Ошибка при сохранении: {str(e)}",
                show_alert=True
            )
    else:
        await callback.answer("⚠️ Ошибка: неверная задача", show_alert=True)


@router.callback_query(F.data.startswith("error_cancel_"))
async def error_cancel(callback: CallbackQuery, state: FSMContext):
    """Отменить добавление ошибки и вернуться к выбору"""
    if not await check_office_worker_rights(callback):
        return
    
    parts = callback.data.split("_")
    task_id = int(parts[2])
    
    data = await state.get_data()
    task_ids = data.get('task_ids', [])
    current_index = data.get('current_task_index', 0)
    
    # Проверяем, что это правильная задача
    if current_index < len(task_ids) and task_ids[current_index] == task_id:
        task = await TaskService.get_task_by_id(task_id)
        task_info = task.get('info', 'Без описания') if task else 'Задача'
        
        # Сбрасываем данные ошибки
        await state.update_data(
            current_error_task_id=task_id,
            current_error_comment=None,
            current_error_photo=None
        )
        
        text = (
            f"❌ <b>Задача не выполнена</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 <b>{task_info}</b>\n\n"
            f"Вы можете добавить комментарий и/или фото к ошибке, или продолжить без деталей."
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_error_options_keyboard(task_id),
            parse_mode="HTML"
        )
        await callback.answer()
    else:
        await callback.answer("⚠️ Ошибка: неверная задача", show_alert=True)


async def complete_check(callback: CallbackQuery, state: FSMContext):
    """Завершить проверку и сохранить результаты"""
    data = await state.get_data()
    form_id = data.get('form_id')
    grades = data.get('grades', [])
    errors_ids = data.get('errors_ids', [])
    part_name = data.get('part_name', 'Блок')
    reviewer_id = str(callback.from_user.id)
    
    if not form_id or not grades:
        await callback.answer("⚠️ Ошибка: данные проверки неполны", show_alert=True)
        await state.clear()
        return
    
    # Сохраняем проверку
    # grades - список оценок (1 или 0)
    # errors_ids - список ID ошибок
    # addition - пустая строка
    try:
        # form_id и reviewer_id должны быть int для базы данных
        check_id = await CheckService.create_check(
            form_id=str(form_id),  # CheckService принимает str, но в БД это INTEGER
            grades=grades,
            errors_ids=errors_ids,  # Теперь используем реальные ID ошибок
            reviewer_id=reviewer_id,  # reviewer_id в БД INTEGER, но передаем как str
            addition=""
        )
        
        # Подсчитываем статистику
        total_tasks = len(grades)
        completed_tasks = sum(grades)
        failed_tasks = total_tasks - completed_tasks
        percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        text = (
            f"✅ <b>Проверка завершена!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏭 Блок: <b>{part_name}</b>\n"
            f"📋 Всего задач: <b>{total_tasks}</b>\n"
            f"✅ Выполнено: <b>{completed_tasks}</b>\n"
            f"❌ Не выполнено: <b>{failed_tasks}</b>\n"
        )
        
        if errors_ids:
            text += f"📝 Ошибок с деталями: <b>{len(errors_ids)}</b>\n"
        
        text += (
            f"📊 Процент выполнения: <b>{percentage:.1f}%</b>\n\n"
            f"Результаты проверки сохранены."
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_check_complete_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("✅ Проверка сохранена!")
        
    except Exception as e:
        await callback.answer(
            f"❌ Ошибка при сохранении проверки: {str(e)}",
            show_alert=True
        )
    
    await state.clear()


@router.callback_query(F.data == "check_back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню"""
    await state.clear()
    from app.keyboards.main_menu import get_main_menu_keyboard
    from app.services.userService import UserService
    
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    access_level = user.get('access_level') if user else UserService.ACCESS_LEVEL_WORKER
    
    await callback.message.edit_text(
        "🏠 <b>Главное меню</b>",
        reply_markup=get_main_menu_keyboard(access_level),
        parse_mode="HTML"
    )
    await callback.answer()

