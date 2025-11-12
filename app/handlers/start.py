from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.services.userService import UserService
from app.states.registration import RegistrationStates

router = Router()


@router.message(CommandStart())
async def send_welcome(message: Message) -> None:
    # Инициализируем базу данных если еще не инициализирована
    await UserService.initialize()
    
    await message.answer("Приветствую! Я бот по контролю производственных процессов на предприятии.")
    user_id = message.from_user.id
    if await UserService.check_user_exist(str(user_id)):
        await message.answer("Добро пожаловать! Используйте доступные команды для работы с ботом.")
    else:
        await message.answer("Пожалуйста, зарегистрируйтесь, чтобы использовать бота. Для этого используйте команду /register.")


@router.message(Command("cancel"))
async def cancel_registration(message: Message, state: FSMContext) -> None:
    """Отмена процесса регистрации"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активного процесса для отмены.")
        return
    
    await state.clear()
    await message.answer("❌ Регистрация отменена. Используйте /register для повторной попытки.")


@router.message(Command("register"))
async def register_user(message: Message, state: FSMContext) -> None:
    # Инициализируем базу данных если еще не инициализирована
    await UserService.initialize()
    
    user_id = message.from_user.id
    if await UserService.check_user_exist(str(user_id)):
        await message.answer("Вы уже зарегистрированы в системе.")
    else:
        await state.set_state(RegistrationStates.waiting_for_fio)
        await message.answer("Введите ваше ФИО (точно как оно указано в базе данных):")


@router.message(RegistrationStates.waiting_for_fio, F.text)
async def process_fio(message: Message, state: FSMContext) -> None:
    """Обработка введенного ФИО пользователя"""
    fio = message.text.strip()
    user_id = message.from_user.id
    
    # Ищем пользователя по ФИО в базе
    users = await UserService.get_user_by_name(fio)
    
    if not users:
        await message.answer(
            "❌ Пользователь с таким ФИО не найден в базе данных.\n"
            "Убедитесь, что вы ввели ФИО правильно, или обратитесь к администратору для добавления вас в систему.\n\n"
            "Попробуйте снова или используйте /cancel для отмены регистрации."
        )
        return
    
    # Если пользователь найден, проверяем, не привязан ли уже к нему другой user_id
    user = users[0]
    if user.get('id') is not None:
        await message.answer(
            "❌ К этому ФИО уже привязан другой Telegram аккаунт.\n"
            "Если это ошибка, обратитесь к администратору."
        )
        await state.clear()
        return
    
    # Привязываем user_id к найденному ФИО
    success = await UserService.update_user_id_by_name(fio, user_id)
    
    if success:
        # Получаем читаемое название роли
        access_level = user.get('access_level', '')
        access_level_name = UserService.get_access_level_name(access_level)
        
        await message.answer(
            f"✅ Регистрация успешно завершена!\n"
            f"Ваше ФИО: {fio}\n"
            f"Уровень доступа: {access_level_name}\n\n"
            f"Теперь вы можете использовать все функции бота."
        )
    else:
        await message.answer(
            "❌ Произошла ошибка при регистрации. Попробуйте позже или обратитесь к администратору."
        )
    
    # Очищаем состояние FSM
    await state.clear()
