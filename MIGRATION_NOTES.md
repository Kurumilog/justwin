# Изменения в системе уровней доступа

## Что изменилось

### 1. Тип данных access_level
- **Было:** INTEGER (0, 1, 2, 3, 4)
- **Стало:** TEXT ('admin', 'manager', 'office_worker', 'leader', 'worker')

### 2. Маппинг старых значений на новые
- 0 → `admin` (Администратор)
- 1 → `manager` (Менеджер)
- 2 → `office_worker` (Офисный работник)
- 3 → `leader` (Руководитель)
- 4 → `worker` (Работник)

## Измененные файлы

### app/db.py
- Изменен тип столбца `access_level` с INTEGER на TEXT
- Добавлен CHECK constraint для валидации значений

### app/services/userService.py
- Добавлены константы для уровней доступа
- Добавлен словарь `ACCESS_LEVEL_NAMES` для перевода на русский
- Добавлен метод `get_access_level_name()` для получения читаемого названия роли
- Обновлен метод `create_user()` с валидацией уровней доступа
- Изменен тип возвращаемого значения `get_user_access_level()` с int на str
- Обновлен метод `get_available_reviewers()` для работы с текстовыми значениями
- Обновлены тестовые данные в `add_sample_users()`

### app/handlers/start.py
- Обновлено отображение уровня доступа при регистрации (теперь показывает читаемое название)

## Новые файлы

### migrate_access_levels.py
- Скрипт для миграции существующих данных
- Автоматически преобразует старые INTEGER значения в TEXT

### check_db.py
- Утилита для проверки данных в базе данных

## Как использовать новые уровни доступа

```python
from app.services.userService import UserService

# Создание пользователя
await UserService.create_user(
    name="Иван Иванов",
    access_level=UserService.ACCESS_LEVEL_ADMIN,
    available=True
)

# Получение читаемого названия роли
level = UserService.ACCESS_LEVEL_MANAGER
name = UserService.get_access_level_name(level)  # "Менеджер"
```

## Константы для использования в коде

```python
UserService.ACCESS_LEVEL_ADMIN          # 'admin'
UserService.ACCESS_LEVEL_MANAGER        # 'manager'
UserService.ACCESS_LEVEL_OFFICE_WORKER  # 'office_worker'
UserService.ACCESS_LEVEL_LEADER         # 'leader'
UserService.ACCESS_LEVEL_WORKER         # 'worker'
```

## Результаты миграции

✅ Успешно мигрированы 3 пользователя:
- Даник: 1 → manager
- Миша: 2 → office_worker
- Илья: 3 → leader
