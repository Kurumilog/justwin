import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers import start

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token="7957057862:AAG7Dcqzd5YNivVm3emjnndJmMcsJdG5omI")
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register handlers
    dp.include_router(start.router)
    
    # Start polling
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

