import asyncio
import aiosqlite


async def add_user_direct_sql():
    """Добавить пользователя прямым SQL запросом"""
    async with aiosqlite.connect('app.db') as conn:
        # INSERT запрос без id (он будет NULL/None)
        await conn.execute(
            """
            INSERT INTO users (id, name, access_level, available)
            VALUES (NULL, ?, ?, ?)
            """,
            ("Алексей Алексеев", "office_worker", 1)
        )
        await conn.commit()
        print("✅ Пользователь добавлен через SQL!")
        
        # Проверяем
        cursor = await conn.execute("SELECT * FROM users WHERE name = ?", ("Алексей Алексеев",))
        user = await cursor.fetchone()
        if user:
            print(f"\nДобавленный пользователь:")
            print(f"  ID: {user[0]}")
            print(f"  ФИО: {user[1]}")
            print(f"  Уровень доступа: {user[2]}")
            print(f"  Доступен: {user[3]}")


if __name__ == "__main__":
    asyncio.run(add_user_direct_sql())
