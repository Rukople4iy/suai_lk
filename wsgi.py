import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config, load_config
import src.handlers.student_echo as student_echo
import src.handlers.admin_echo as admin_echo
import src.handlers.guest_echo as guest_echo
import src.handlers.teacher_echo as teacher_echo
from src.db.db import init_db
from src.db.models import Base

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )

    logging.info("Starting bot")
    init_db(Base)
    config: Config = load_config()

    bot_main = Bot(token=config.tg_bot_main.token)
    storage = MemoryStorage()
    dp_main = Dispatcher(bot=bot_main, storage=storage)

    dp_main.include_router(student_echo.router_main)
    dp_main.include_router(admin_echo.router_main)
    dp_main.include_router(guest_echo.router_main)
    dp_main.include_router(teacher_echo.router_main)
    await bot_main.delete_webhook(drop_pending_updates=True)
    await dp_main.start_polling(bot_main)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
