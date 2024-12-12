from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import src.db.crud.common_crud as crud
import src.keyboards.kb as kb
from functools import wraps
from aiogram.types import Message
from src.db.crud.common_crud import get_user_by_telegram_id
import logging

logging.basicConfig(level=logging.INFO)

router_main: Router = Router()





def require_role(role):
    def decorator(handler):
        @wraps(handler)
        async def wrapper(message: Message, *args, **kwargs):
            user = get_user_by_telegram_id(str(message.from_user.id))
            logging.info(f"user check: {user.role, role}")
            if user.role == role:
                return await handler(message, *args, **kwargs)
            else:
                await message.answer("У вас нет прав для выполнения этого действия.")
        return wrapper
    return decorator
