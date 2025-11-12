import asyncio
import aiosqlite


async def check_users():
    async with aiosqlite.connect('app.db') as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute('SELECT * FROM users')
        rows = await cursor.fetchall()
        
        print('\n✅ Пользователи в базе данных:')
        print('-' * 80)
        for row in rows:
            user = dict(row)
            print(f"  ФИО: {user.get('name', 'N/A')}")
            print(f"  User ID: {user.get('id', 'не привязан')}")
            print(f"  Уровень доступа: {user.get('access_level', 'N/A')}")
            print(f"  Доступен: {user.get('available', 'N/A')}")
            print('-' * 80)


if __name__ == "__main__":
    asyncio.run(check_users())
