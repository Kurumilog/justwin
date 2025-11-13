# Примеры использования клавиатур

## Структура клавиатур

### 1. Главное меню (`main_menu.py`)

**Для всех пользователей:**
- 📋 Мои проверки
- ❓ Помощь

**Для ADMIN и MANAGER (дополнительно):**
- 📝 Управление задачами
- 📄 Управление формами

**Для OFFICE_WORKER, MANAGER, ADMIN (дополнительно):**
- ✅ Провести проверку
- 📊 Отчеты

### 2. Управление задачами (`task_keyboards.py`)

**Доступно только для ADMIN и MANAGER**

Функции:
- Создание новых задач
- Просмотр списка задач
- Редактирование задач
- Удаление задач (с подтверждением)
- Поиск задач

### 3. Управление формами (`form_keyboards.py`)

**Доступно только для ADMIN и MANAGER**

Функции:
- Создание новых форм
- Просмотр списка форм
- Редактирование названия, задач и дополнительной информации
- Добавление/удаление задач в форме (с чекбоксами)
- Удаление форм (с подтверждением)
- Поиск форм

### 4. Проверки (`check_keyboards.py`)

**Доступно для OFFICE_WORKER, MANAGER, ADMIN**

Функции:
- Проведение новой проверки
- Выбор формы для проверки
- Выставление оценок (✅ Выполнено / ❌ Не выполнено)
- Добавление ошибок с комментариями и фото
- Просмотр истории проверок
- Статистика проверок

---

## Примеры использования в коде

### Показ главного меню

```python
from app.keyboards import get_main_menu_keyboard
from app.services.userService import UserService

access_level = await UserService.get_user_access_level(str(user_id))
await message.answer(
    "📋 Главное меню:",
    reply_markup=get_main_menu_keyboard(access_level)
)
```

### Управление задачами

```python
from app.keyboards import (
    get_task_management_keyboard,
    get_task_list_keyboard,
    get_task_actions_keyboard
)

# Показать меню управления задачами
await callback.message.edit_text(
    "📝 Управление задачами:",
    reply_markup=get_task_management_keyboard()
)

# Показать список задач
tasks = await TaskService.get_all_tasks()
await callback.message.edit_text(
    "📋 Список задач:",
    reply_markup=get_task_list_keyboard(tasks)
)

# Показать действия для конкретной задачи
await callback.message.edit_text(
    f"Задача: {task_info}",
    reply_markup=get_task_actions_keyboard(task_id)
)
```

### Управление формами

```python
from app.keyboards import (
    get_form_management_keyboard,
    get_form_list_keyboard,
    get_form_task_selection_keyboard
)

# Показать меню управления формами
await callback.message.edit_text(
    "📄 Управление формами:",
    reply_markup=get_form_management_keyboard()
)

# Показать список форм
forms = await FormService.get_all_forms()
await callback.message.edit_text(
    "📋 Список форм:",
    reply_markup=get_form_list_keyboard(forms)
)

# Выбор задач для формы (с чекбоксами)
tasks = await TaskService.get_all_tasks()
selected_ids = [1, 3, 5]  # ID уже выбранных задач
await callback.message.edit_text(
    "Выберите задачи для формы:",
    reply_markup=get_form_task_selection_keyboard(tasks, selected_ids, form_id)
)
```

### Проведение проверок

```python
from app.keyboards import (
    get_form_selection_keyboard,
    get_check_grade_keyboard,
    get_check_complete_keyboard
)

# Выбор формы для проверки
forms = await FormService.get_all_forms()
await callback.message.edit_text(
    "Выберите форму для проверки:",
    reply_markup=get_form_selection_keyboard(forms)
)

# Оценка задачи в процессе проверки
await message.answer(
    f"Задача {current_num} из {total}: {task_info}",
    reply_markup=get_check_grade_keyboard(task_id, current_num, total)
)

# Завершение проверки
await message.answer(
    "✅ Проверка успешно завершена!",
    reply_markup=get_check_complete_keyboard(check_id)
)
```

---

## Callback data паттерны

### Задачи
- `task_create` - создать задачу
- `task_list` - показать список задач
- `task_view_{id}` - посмотреть задачу
- `task_edit_{id}` - редактировать задачу
- `task_delete_{id}` - удалить задачу
- `task_delete_confirm_{id}` - подтвердить удаление

### Формы
- `form_create` - создать форму
- `form_list` - показать список форм
- `form_view_{id}` - посмотреть форму
- `form_edit_{id}` - редактировать форму
- `form_edit_name_{id}` - редактировать название
- `form_edit_addition_{id}` - редактировать доп. информацию
- `form_tasks_{id}` - управление задачами формы
- `form_task_toggle_{form_id}_{task_id}` - переключить задачу
- `form_tasks_save_{id}` - сохранить задачи формы
- `form_delete_{id}` - удалить форму
- `form_delete_confirm_{id}` - подтвердить удаление

### Проверки
- `check_new` - начать новую проверку
- `check_form_{id}` - выбрать форму для проверки
- `check_grade_{task_id}_pass` - оценка "выполнено"
- `check_grade_{task_id}_fail` - оценка "не выполнено"
- `check_complete_{id}` - завершить проверку
- `check_view_{id}` - посмотреть проверку
- `check_cancel` - отменить проверку
- `check_cancel_confirm` - подтвердить отмену

### Общие
- `main_menu` - вернуться в главное меню
- `my_checks` - мои проверки
- `help` - помощь
