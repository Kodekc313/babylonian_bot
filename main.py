# main.py
import asyncio
import logging
import ssl

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
# --- Добавляем импорты для FSM ---
from aiogram.fsm.storage.memory import MemoryStorage

# Импортируем конфигурацию (токен)
from config import BOT_TOKEN
# Импортируем роутер из обработчиков
from handlers import router # Убедитесь, что здесь импортируется ваш основной роутер из handlers.py
# Импортируем функции базы данных
from database import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    """Основная функция запуска бота."""
    # --- Инициализация базы данных ---
    init_db()
    
    # --- Создаем хранилище для FSM ---
    storage = MemoryStorage()

    # Создаем бота с нашим SSL контекстом через модификацию _connector_init
    from aiogram.client.session.aiohttp import AiohttpSession
    import ssl
    import certifi
    
    session = AiohttpSession()
    # Модифицируем внутренний словарь инициализации коннектора
    session._connector_init["ssl"] = False  # Отключаем проверку SSL для обхода проблем
    
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session
    )

    # --- Создаем диспетчер и передаем ему хранилище ---
    dp = Dispatcher(storage=storage)

    # Включаем роутер из handlers.py
    dp.include_router(router)

    # Удаляем вебхук перед запуском полинга
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Webhook удален (если был). Начинаем polling...")

    # Запускаем получение обновлений
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Произошла ошибка при запуске бота: {e}")
    finally:
        if bot.session:
             await bot.session.close()
        logging.info("Сессия бота закрыта.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен вручную.")
    except ValueError as ve:
        logging.error(ve)
    except Exception as e:
        logging.error(f"Критическая ошибка при инициализации: {e}")