import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config, load_config
from src.handlers import echo
from src.db.db import init_db

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )

    logging.info("Starting bot")
    init_db()
    config: Config = load_config()

    bot_main = Bot(token=config.tg_bot_main.token)
    storage = MemoryStorage()
    dp_main = Dispatcher(bot=bot_main, storage=storage)

    dp_main.include_router(echo.router_main)
    await bot_main.delete_webhook(drop_pending_updates=True)
    await dp_main.start_polling(bot_main)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
