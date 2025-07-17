import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, DATABASE_PATH
from database.db import Database

# Импортируем роутеры
from handlers import common, funeral, ai_lawyer, shop, memory
from handlers import registration
from handlers import voice


async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info('=== Запуск Telegram-бота ===')

    # Инициализация бота и хранилища состояний
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Инициализация базы данных
    db = Database(DATABASE_PATH)
    logger.info('База данных инициализирована')

    # Middleware для передачи базы данных в хендлеры
    async def db_middleware(handler, event, data):
        data["db"] = db
        return await handler(event, data)

    dp.message.middleware(db_middleware)
    dp.callback_query.middleware(db_middleware)

    # ❗ Правильный порядок подключения роутеров
    logger.info('Регистрируем роутеры...')
    dp.include_router(common.router)         # /start ОБЯЗАТЕЛЬНО первым!
    dp.include_router(funeral.router)
    dp.include_router(ai_lawyer.router)
    dp.include_router(shop.router)
    dp.include_router(memory.router)
    dp.include_router(registration.router)
    dp.include_router(voice.router)
    logger.info('Роутеры успешно зарегистрированы')

    # Установка команд бота
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="services", description="Организация похорон"),
        BotCommand(command="shop", description="Товары"),
        BotCommand(command="memory", description="Уголок памяти"),
        BotCommand(command="ask_lawyer", description="AI-помощник по документам"),
        BotCommand(command="help", description="Помощь")
    ])
    logger.info('Команды Telegram-бота установлены')

    print("✅ Бот запущен!")
    logger.info('=== Бот запущен и ожидает сообщений ===')
    await dp.start_polling(bot)


if __name__ == "__main__":
    print(f"BOT_TOKEN = '{BOT_TOKEN}'")

    asyncio.run(main())

