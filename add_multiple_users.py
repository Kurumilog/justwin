import asyncio
from app.services.userService import UserService


async def add_multiple_users():
    """Добавить несколько пользователей в базу данных"""
    await UserService.initialize()
    
    # Список пользователей для добавления
    users_to_add = [
        {
            "name": "Иван Иванов",
            "access_level": UserService.ACCESS_LEVEL_OFFICE_WORKER,
            "available": True
        },
        {
            "name": "Петр Петров", 
            "access_level": UserService.ACCESS_LEVEL_LEADER,
            "available": True
        },
        {
            "name": "Сергей Сергеев",
            "access_level": UserService.ACCESS_LEVEL_WORKER,
            "available": True
        },
        {
            "name": "Илья Ильин",
            "access_level": UserService.ACCESS_LEVEL_ADMIN,
            "available": True
        },
        {
            "name": "smt",
            "access_level": UserService.ACCESS_LEVEL_ADMIN,
            "available": True
        }
    ]
    
    print("Добавление пользователей...\n")
    
    for user_data in users_to_add:
        try:
            user_id = await UserService.create_user(**user_data)
            print(f"✅ Добавлен: {user_data['name']} ({user_data['access_level']})")
        except Exception as e:
            print(f"❌ Ошибка при добавлении {user_data['name']}: {e}")
    
    print("\n" + "="*80)
    print("Все пользователи в базе:")
    print("="*80 + "\n")
    
    # Показать всех пользователей
    users = await UserService.get_user_by_name("")
    all_users = await UserService.db.get_all("users")
    
    for user in all_users:
        access_name = UserService.get_access_level_name(user.get('access_level', ''))
        print(f"ФИО: {user.get('name')}")
        print(f"  Telegram ID: {user.get('id', 'не привязан')}")
        print(f"  Уровень доступа: {access_name} ({user.get('access_level')})")
        print(f"  Доступен: {'Да' if user.get('available') else 'Нет'}")
        print()


if __name__ == "__main__":
    asyncio.run(add_multiple_users())
