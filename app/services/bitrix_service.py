# app/services/bitrix_service.py
from typing import List, Dict, Optional
from fast_bitrix24 import Bitrix
from config import BITRIX_WEBHOOK

# Убедитесь, что вы создали эти поля в CRM -> Настройки -> Свои поля -> Контакты
# https://helpdesk.bitrix24.ru/open/12524244/
TELEGRAM_ID_FIELD = 'UF_CRM_TELEGRAM_ID'
ACCESS_LEVEL_FIELD = 'UF_CRM_ACCESS_LEVEL'
AVAILABLE_FIELD = 'UF_CRM_AVAILABLE'


class BitrixService:
    b = None
    initialized = False

    # Константы уровней доступа
    ACCESS_LEVEL_ADMIN = 'admin'
    ACCESS_LEVEL_MANAGER = 'manager'
    ACCESS_LEVEL_OFFICE_WORKER = 'office_worker'
    ACCESS_LEVEL_LEADER = 'leader'
    ACCESS_LEVEL_WORKER = 'worker'

    # Перевод уровней доступа на русский
    ACCESS_LEVEL_NAMES = {
        'admin': 'Администратор',
        'manager': 'Менеджер',
        'office_worker': 'Офисный работник',
        'leader': 'Руководитель',
        'worker': 'Работник'
    }

    @staticmethod
    async def initialize():
        """Инициализировать подключение к Bitrix24"""
        if not BitrixService.initialized:
            if not BITRIX_WEBHOOK or BITRIX_WEBHOOK == "YOUR_BITRIX_WEBHOOK_URL":
                raise ValueError("Необходимо указать BITRIX_WEBHOOK в файле config.py")
            BitrixService.b = Bitrix(BITRIX_WEBHOOK)
            BitrixService.initialized = True

    @staticmethod
    def get_access_level_name(access_level: str) -> str:
        """Получить русское название уровня доступа"""
        return BitrixService.ACCESS_LEVEL_NAMES.get(access_level, access_level)

    @staticmethod
    async def check_user_exist(user_id: str) -> bool:
        """Проверить существование пользователя по Telegram ID"""
        users = await BitrixService.b.get_all(
            'crm.contact.list',
            params={
                'filter': {TELEGRAM_ID_FIELD: user_id},
                'select': ['ID']
            }
        )
        return bool(users)

    @staticmethod
    async def get_user_by_name(name: str) -> List[Dict]:
        """Найти пользователя по имени (ФИО)"""
        # Bitrix24 ищет по частичному совпадению в полях имени, фамилии
        contacts = await BitrixService.b.get_all(
            'crm.contact.list',
            params={
                'filter': {'%NAME': name},
                'select': ['ID', 'NAME', 'LAST_NAME', 'SECOND_NAME', TELEGRAM_ID_FIELD, ACCESS_LEVEL_FIELD]
            }
        )
        # Преобразуем в формат, похожий на старый сервис
        return [
            {
                'id': contact.get(TELEGRAM_ID_FIELD),
                'name': f"{contact.get('LAST_NAME', '')} {contact.get('NAME', '')} {contact.get('SECOND_NAME', '')}".strip(),
                'access_level': contact.get(ACCESS_LEVEL_FIELD),
                'bitrix_id': contact['ID']
            } for contact in contacts
        ]

    @staticmethod
    async def update_user_id_by_name(name: str, user_id: str) -> bool:
        """Привязать Telegram ID к контакту в Bitrix по имени"""
        # Находим контакт по имени
        users = await BitrixService.get_user_by_name(name)
        if not users:
            return False

        # Предполагаем, что ФИО уникально
        contact_to_update = users[0]
        bitrix_id = contact_to_update.get('bitrix_id')

        if not bitrix_id:
            return False

        # Обновляем поле с Telegram ID
        await BitrixService.b.call(
            'crm.contact.update',
            items={
                'ID': bitrix_id,
                'fields': {
                    TELEGRAM_ID_FIELD: user_id
                }
            }
        )
        return True

    # Методы-заглушки, которые нужно будет реализовать при необходимости
    @staticmethod
    async def create_user(name: str, access_level: str, available: bool = True) -> int:
        """Создать нового пользователя (контакт в Bitrix)"""
        # Эта логика может быть сложнее (парсинг ФИО)
        # Для простоты пока используем только имя
        await BitrixService.b.call(
            'crm.contact.add',
            items={
                'fields': {
                    'NAME': name,
                    ACCESS_LEVEL_FIELD: access_level,
                    AVAILABLE_FIELD: 'Y' if available else 'N'
                }
            }
        )
        return 1 # Возвращаем условный ID

    @staticmethod
    async def get_user_access_level(user_id: str) -> Optional[str]:
        """Получить уровень доступа пользователя по Telegram ID"""
        users = await BitrixService.b.get_all(
            'crm.contact.list',
            params={
                'filter': {TELEGRAM_ID_FIELD: user_id},
                'select': [ACCESS_LEVEL_FIELD]
            }
        )
        if users:
            return users[0].get(ACCESS_LEVEL_FIELD)
        return None
