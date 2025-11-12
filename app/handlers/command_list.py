from aiogram import Router
from aiogram.types import Message

def command_list(router: Router) -> None:
    async def cmd_list(message: Message):
        """Список допустимых команд"""
        await message.answer("Вот список доступных команд:\n/start - Запустить бота\n/list - Показать этот список команд\n/help - Получить помощь по использованию бота")
        
