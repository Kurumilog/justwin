import asyncio
from app.services.userService import UserService


async def add_user():
    """Добавить нового пользователя в базу данных"""
    await UserService.initialize()
    
    # Добавляем пользователя Даник с уровнем доступа manager
    user_id = await UserService.create_user(
        name="Даник",
        access_level=UserService.ACCESS_LEVEL_MANAGER,
        available=True
    )
    
    print(f"✅ Пользователь добавлен с ID: {user_id}")
    
    # Проверяем, что пользователь добавлен
    users = await UserService.get_user_by_name("Даник")
    for user in users:
        print(f"\nДанные пользователя:")
        print(f"  ФИО: {user.get('name')}")
        print(f"  Telegram ID: {user.get('id', 'не привязан')}")
        print(f"  Уровень доступа: {user.get('access_level')}")
        print(f"  Доступен: {user.get('available')}")


if __name__ == "__main__":
    asyncio.run(add_user())
