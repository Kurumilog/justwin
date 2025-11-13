import asyncio
import aiosqlite


async def reset_user_ids():
    """Обнулить id (Telegram ID) для всех пользователей в таблице users"""
    async with aiosqlite.connect('app.db') as conn:
        # Обнуляем id для всех пользователей
        cursor = await conn.execute('UPDATE users SET id = NULL')
        await conn.commit()
        
        affected_rows = cursor.rowcount
        print(f'✅ Обнулено id для {affected_rows} пользователей')
        
        # Показываем результат
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute('SELECT name, id, access_level FROM users')
        rows = await cursor.fetchall()
        
        print('\n📋 Текущее состояние пользователей:')
        print('-' * 80)
        for row in rows:
            user = dict(row)
            print(f"  ФИО: {user.get('name', 'N/A')}")
            print(f"  User ID: {user.get('id', 'не привязан')}")
            print(f"  Уровень доступа: {user.get('access_level', 'N/A')}")
            print('-' * 80)


if __name__ == "__main__":
    asyncio.run(reset_user_ids())

