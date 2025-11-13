# app/handlers/leader.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.services.userService import UserService
from app.services.checkService import CheckService
from app.services.formService import FormService
from app.keyboards.leader_keyboards import (
    get_leader_cabinet_keyboard,
    get_workers_list_keyboard,
    get_brigade_errors_keyboard
)

router = Router()


async def check_leader_rights(user_id: int) -> bool:
    """Проверка прав LEADER"""
    access_level = await UserService.get_user_access_level(str(user_id))
    return access_level == UserService.ACCESS_LEVEL_LEADER


@router.callback_query(F.data == "leader_cabinet")
async def show_leader_cabinet(callback: CallbackQuery, state: FSMContext) -> None:
    """Показать личный кабинет руководителя бригады"""
    await state.clear()
    
    if not await check_leader_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    # Получаем информацию о руководителе
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    part_name = user.get('part_name', 'Не назначена') if user else 'Не назначена'
    name = user.get('name', 'Руководитель') if user else 'Руководитель'
    
    await callback.message.edit_text(
        f"👔 <b>Личный кабинет руководителя</b>\n\n"
        f"<b>ФИО:</b> {name}\n"
        f"<b>Бригада:</b> {part_name}\n\n"
        f"Здесь вы можете:\n"
        f"• Просматривать список своих подчиненных\n"
        f"• Отслеживать ошибки бригады",
        reply_markup=get_leader_cabinet_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "leader_view_workers")
async def view_workers(callback: CallbackQuery, state: FSMContext) -> None:
    """Просмотр подчиненных работников"""
    if not await check_leader_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    # Получаем бригаду лидера
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    part_name = user.get('part_name') if user else None
    
    if not part_name:
        await callback.message.edit_text(
            "⚠️ <b>Бригада не назначена</b>\n\n"
            "Вы не назначены руководителем какой-либо бригады.\n"
            "Обратитесь к администратору.",
            reply_markup=get_leader_cabinet_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # Получаем работников бригады
    workers = await UserService.get_workers_by_part_name(part_name)
    
    workers_text = f"👥 <b>Подчиненные бригады \"{part_name}\"</b>\n\n"
    
    if workers:
        workers_text += f"<b>Всего работников:</b> {len(workers)}\n\n"
        for i, worker in enumerate(workers, 1):
            name = worker.get('name', 'Без имени')
            available = "✅ Доступен" if worker.get('available') else "❌ Недоступен"
            telegram_id = worker.get('id', 'не привязан')
            workers_text += f"{i}. <b>{name}</b>\n"
            workers_text += f"   Статус: {available}\n"
            workers_text += f"   Telegram ID: {telegram_id}\n\n"
    else:
        workers_text += "⚠️ В бригаде пока нет работников"
    
    await callback.message.edit_text(
        workers_text,
        reply_markup=get_workers_list_keyboard(workers),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "leader_view_errors")
async def view_brigade_errors(callback: CallbackQuery, state: FSMContext) -> None:
    """Просмотр ошибок бригады"""
    if not await check_leader_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    # Получаем бригаду лидера
    user = await UserService.get_user_by_id(str(callback.from_user.id))
    part_name = user.get('part_name') if user else None
    
    if not part_name:
        await callback.message.edit_text(
            "⚠️ <b>Бригада не назначена</b>\n\n"
            "Вы не назначены руководителем какой-либо бригады.\n"
            "Обратитесь к администратору.",
            reply_markup=get_leader_cabinet_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # Получаем форму по part_name
    forms = await FormService.get_all_forms()
    brigade_form = next((f for f in forms if f.get('part_name') == part_name), None)
    
    if not brigade_form:
        await callback.message.edit_text(
            f"⚠️ <b>Форма не найдена</b>\n\n"
            f"Для бригады \"{part_name}\" не создана форма проверок.\n"
            f"Обратитесь к менеджеру.",
            reply_markup=get_leader_cabinet_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # Получаем ошибки бригады
    errors = await CheckService.get_errors_by_form(brigade_form.get('id'))
    
    errors_text = f"⚠️ <b>Ошибки бригады \"{part_name}\"</b>\n\n"
    
    if errors:
        errors_text += f"<b>Всего ошибок:</b> {len(errors)}\n\n"
        
        # Показываем последние 10 ошибок
        for i, error in enumerate(errors[:10], 1):
            comment = error.get('comment', 'Без описания')
            checked_at = error.get('checked_at', 'Неизвестно')
            errors_text += f"{i}. <b>Дата:</b> {checked_at}\n"
            errors_text += f"   <b>Описание:</b> {comment[:100]}\n"
            if error.get('photo_url'):
                errors_text += f"   📷 Есть фото\n"
            errors_text += "\n"
        
        if len(errors) > 10:
            errors_text += f"<i>... и еще {len(errors) - 10} ошибок</i>\n"
    else:
        errors_text += "✅ Ошибок не обнаружено!\n\n"
        errors_text += "Ваша бригада работает отлично! 🎉"
    
    await callback.message.edit_text(
        errors_text,
        reply_markup=get_brigade_errors_keyboard(len(errors) > 0),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("worker_info_"))
async def show_worker_info(callback: CallbackQuery) -> None:
    """Показать информацию о конкретном работнике"""
    if not await check_leader_rights(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав доступа", show_alert=True)
        return
    
    worker_name = callback.data.split("_", 2)[2]
    
    # Получаем информацию о работнике
    users = await UserService.get_user_by_name(worker_name)
    if not users:
        await callback.answer("❌ Работник не найден", show_alert=True)
        return
    
    worker = users[0]
    name = worker.get('name', 'Без имени')
    available = "✅ Доступен" if worker.get('available') else "❌ Недоступен"
    telegram_id = worker.get('id', 'не привязан')
    part_name = worker.get('part_name', 'Не назначен')
    
    info_text = (
        f"👷 <b>Информация о работнике</b>\n\n"
        f"<b>ФИО:</b> {name}\n"
        f"<b>Бригада:</b> {part_name}\n"
        f"<b>Статус:</b> {available}\n"
        f"<b>Telegram ID:</b> {telegram_id}\n"
    )
    
    await callback.answer(info_text, show_alert=True)
