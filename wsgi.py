import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import Config, load_config
from src.handlers import echo

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s "
        "[%(asctime)s] - %(name)s - %(message)s",
    )

    logger.info("Starting bot")

    config: Config = load_config()

    bot_main = Bot(token=config.tg_bot_main.token)
    dp_main = Dispatcher(bot=bot_main)

    dp_main.include_router(echo.router_main)
    await bot_main.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(
        dp_main.start_polling(bot_main)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")


