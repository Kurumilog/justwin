import asyncio
import time
from app.services.userService import UserService
from app.services.taskService import TaskService
from app.services.formService import FormService


async def setup_user_and_form():
    """Установить part_name для пользователя, создать задачи и форму"""
    
    # Инициализация сервисов
    await UserService.initialize()
    await TaskService.initialize()
    await FormService.initialize()
    
    user_id = "936734087"
    part_name = "новый цех"
    
    print("=" * 80)
    print("Настройка пользователя и создание формы")
    print("=" * 80)
    print()
    
    # 1. Обновляем part_name для пользователя
    print(f"1. Обновление part_name для пользователя {user_id}...")
    user = await UserService.get_user_by_id(user_id)
    if not user:
        print(f"❌ Пользователь с ID {user_id} не найден!")
        return
    
    result = await UserService.update_user_part_name(user_id, part_name)
    if result:
        print(f"✅ part_name установлен: '{part_name}'")
        print(f"   Пользователь: {user.get('name', 'N/A')}")
    else:
        print(f"❌ Ошибка при обновлении part_name")
        return
    
    print()
    
    # 2. Создаем 5 новых задач (с уникальными названиями)
    print("2. Создание задач...")
    timestamp = int(time.time())
    
    task_descriptions = [
        f"Проверка оборудования [{timestamp}]",
        f"Контроль качества продукции [{timestamp}]",
        f"Проверка техники безопасности [{timestamp}]",
        f"Инвентаризация материалов [{timestamp}]",
        f"Проверка документации [{timestamp}]"
    ]
    
    created_task_ids = []
    for i, task_info in enumerate(task_descriptions, 1):
        try:
            task_id = await TaskService.create_task(task_info)
            created_task_ids.append(task_id)
            print(f"   ✅ Задача {i} создана (ID: {task_id}): {task_info}")
        except Exception as e:
            # Если задача уже существует, попробуем найти её
            all_tasks = await TaskService.get_all_tasks()
            existing_task = next((t for t in all_tasks if t.get('info') == task_info), None)
            if existing_task:
                task_id = existing_task.get('id')
                created_task_ids.append(task_id)
                print(f"   ℹ️  Задача {i} уже существует (ID: {task_id}): {task_info}")
            else:
                print(f"   ❌ Ошибка при создании задачи '{task_info}': {e}")
    
    if not created_task_ids:
        print("❌ Не удалось получить ни одной задачи!")
        return
    
    print(f"\n   Всего задач для формы: {len(created_task_ids)}")
    print()
    
    # 3. Создаем форму с этими задачами
    print(f"3. Создание формы с part_name '{part_name}'...")
    try:
        form_id = await FormService.create_form(part_name, tasks=created_task_ids)
        print(f"✅ Форма создана (ID: {form_id})")
        print(f"   part_name: {part_name}")
        print(f"   Задачи в форме: {', '.join(map(str, created_task_ids))}")
    except Exception as e:
        # Если форма уже существует, обновляем её задачи
        existing_form = await FormService.get_form_by_part_name(part_name)
        if existing_form:
            form_id = existing_form.get('id')
            await FormService.update_form_tasks(form_id, created_task_ids)
            print(f"✅ Форма обновлена (ID: {form_id})")
            print(f"   part_name: {part_name}")
            print(f"   Задачи в форме: {', '.join(map(str, created_task_ids))}")
        else:
            print(f"❌ Ошибка при создании формы: {e}")
            return
    
    print()
    print("=" * 80)
    print("✅ Готово! Все операции выполнены успешно.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(setup_user_and_form())

