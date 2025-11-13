import asyncio
from app.services.userService import UserService
from app.db import Database

async def db_start():
    """Инициализация SQLite базы данных"""
    print("Инициализация базы данных...")
    db = Database()
    await UserService.initialize()
    print("✅ База данных успешно инициализирована!")

if __name__ == "__main__":
    asyncio.run(db_start())