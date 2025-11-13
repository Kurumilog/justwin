# app/handlers/worker.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.services.userService import UserService
from app.services.formService import FormService
from app.services.checkService import CheckService
from app.keyboards.worker_keyboards import get_worker_cabinet_keyboard, get_worker_checks_keyboard

router = Router()


async def check_worker_rights(callback: CallbackQuery) -> bool:
    """Проверить, является ли пользователь работником"""
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    if not user or user.get('access_level') != 'worker':
        await callback.answer("⛔ У вас нет доступа к этому разделу", show_alert=True)
        return False
    return True


@router.callback_query(F.data == "worker_cabinet")
async def show_worker_cabinet(callback: CallbackQuery):
    """Показать личный кабинет работника"""
    if not await check_worker_rights(callback):
        return
    
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    username = user.get('name', 'Работник')
    part_name = user.get('part_name', 'Не назначена')
    
    # Получаем форму бригады
    form = None
    if part_name and part_name != 'Не назначена':
        form = await FormService.get_form_by_part_name(part_name)
    
    text = (
        f"👷 <b>Личный кабинет работника</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 {username}\n"
        f"🔑 Роль: <code>Работник</code>\n"
        f"🏭 Бригада: <b>{part_name}</b>\n"
    )
    
    if form:
        text += f"\n📋 Информация о бригаде доступна"
    else:
        text += f"\n⚠️ Бригада не найдена в системе"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_worker_cabinet_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "worker_view_brigade_info")
async def view_brigade_info(callback: CallbackQuery):
    """Просмотр информации о бригаде"""
    if not await check_worker_rights(callback):
        return
    
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    part_name = user.get('part_name')
    
    if not part_name:
        await callback.answer("⚠️ Вы не назначены в бригаду", show_alert=True)
        return
    
    # Получаем форму бригады
    form = await FormService.get_form_by_part_name(part_name)
    
    if not form:
        await callback.message.edit_text(
            f"⚠️ <b>Бригада не найдена</b>\n\n"
            f"Бригада <b>{part_name}</b> не зарегистрирована в системе.",
            reply_markup=get_worker_cabinet_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # Получаем список работников этой бригады
    workers = await UserService.get_workers_by_part_name(part_name)
    
    text = (
        f"🏭 <b>Информация о бригаде</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 Название: <b>{part_name}</b>\n"
        f"👥 Работников: <b>{len(workers)}</b>\n\n"
    )
    
    if workers:
        text += "👷 <b>Состав бригады:</b>\n"
        for idx, worker in enumerate(workers, 1):
            name = worker.get('name', 'Без имени')
            available = "✅" if worker.get('available') else "❌"
            text += f"{idx}. {available} {name}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_worker_cabinet_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "worker_view_grades")
async def view_brigade_grades(callback: CallbackQuery):
    """Просмотр оценок бригады"""
    if not await check_worker_rights(callback):
        return
    
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    part_name = user.get('part_name')
    
    if not part_name:
        await callback.answer("⚠️ Вы не назначены в бригаду", show_alert=True)
        return
    
    # Получаем форму бригады
    form = await FormService.get_form_by_part_name(part_name)
    
    if not form:
        await callback.message.edit_text(
            f"⚠️ <b>Бригада не найдена</b>\n\n"
            f"Бригада <b>{part_name}</b> не зарегистрирована в системе.",
            reply_markup=get_worker_cabinet_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    form_id = form.get('id')
    
    # Получаем все проверки для этой формы
    checks = await CheckService.get_checks_by_form(form_id)
    
    if not checks:
        await callback.message.edit_text(
            f"📊 <b>Оценки бригады</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏭 Бригада: <b>{part_name}</b>\n\n"
            f"⚠️ Проверки еще не проводились",
            reply_markup=get_worker_checks_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # Вычисляем средний балл
    total_score = 0
    check_count = len(checks)
    
    text = (
        f"📊 <b>Оценки бригады</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏭 Бригада: <b>{part_name}</b>\n"
        f"📋 Проведено проверок: <b>{check_count}</b>\n\n"
    )
    
    # Показываем последние 10 проверок
    recent_checks = checks[-10:] if len(checks) > 10 else checks
    recent_checks.reverse()
    
    for check in recent_checks:
        check_id = check.get('id')
        checked_at = check.get('checked_at', 'Неизвестно')
        grades_str = check.get('grades', '')
        
        # Парсим оценки
        if grades_str:
            grades = [int(x.strip()) for x in grades_str.split(',') if x.strip().isdigit()]
            if grades:
                # Вычисляем процент выполнения
                completed_tasks = sum(1 for g in grades if g == 1)
                total_tasks = len(grades)
                percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                
                # Вычисляем балл по шестибалльной шкале
                score = round(percentage / 100 * 6, 1)
                total_score += score
                
                # Эмодзи в зависимости от балла
                if score >= 5.5:
                    emoji = "🟢"
                elif score >= 4.0:
                    emoji = "🟡"
                else:
                    emoji = "🔴"
                
                text += (
                    f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📅 {checked_at[:16]}\n"
                    f"{emoji} Балл: <b>{score}/6</b> ({percentage:.0f}%)\n"
                    f"✅ Выполнено: {completed_tasks}/{total_tasks} задач\n"
                )
    
    # Средний балл
    if check_count > 0:
        avg_score = total_score / check_count
        text += (
            f"\n━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📈 <b>Средний балл: {avg_score:.2f}/6</b>\n"
        )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_worker_checks_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "worker_view_errors")
async def view_brigade_errors(callback: CallbackQuery):
    """Просмотр ошибок бригады"""
    if not await check_worker_rights(callback):
        return
    
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    part_name = user.get('part_name')
    
    if not part_name:
        await callback.answer("⚠️ Вы не назначены в бригаду", show_alert=True)
        return
    
    # Получаем форму бригады
    form = await FormService.get_form_by_part_name(part_name)
    
    if not form:
        await callback.message.edit_text(
            f"⚠️ <b>Бригада не найдена</b>\n\n"
            f"Бригада <b>{part_name}</b> не зарегистрирована в системе.",
            reply_markup=get_worker_cabinet_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    form_id = form.get('id')
    
    # Получаем ошибки по форме
    errors = await CheckService.get_errors_by_form(form_id)
    
    if not errors:
        await callback.message.edit_text(
            f"✅ <b>Ошибки бригады</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏭 Бригада: <b>{part_name}</b>\n\n"
            f"🎉 Отлично! Ошибок не обнаружено!",
            reply_markup=get_worker_checks_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    text = (
        f"❌ <b>Ошибки бригады</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏭 Бригада: <b>{part_name}</b>\n"
        f"📋 Всего ошибок: <b>{len(errors)}</b>\n\n"
    )
    
    # Показываем последние 10 ошибок
    recent_errors = errors[-10:] if len(errors) > 10 else errors
    recent_errors.reverse()
    
    for idx, error in enumerate(recent_errors, 1):
        error_id = error.get('id')
        comment = error.get('comment', 'Без комментария')
        photo_url = error.get('photo_url')
        
        text += (
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔢 Ошибка #{error_id}\n"
            f"📝 {comment}\n"
        )
        
        if photo_url:
            text += f"📷 Есть фото\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_worker_checks_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
