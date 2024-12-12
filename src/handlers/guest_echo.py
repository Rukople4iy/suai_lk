from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import src.db.crud.common_crud as crud
import src.keyboards.student_kb as student
import src.keyboards.teacher_kb as teacher

router_main: Router = Router()

# Хэндлер для команды /start
@router_main.message(CommandStart())
async def send_welcome(message: Message):
    user = crud.get_user_by_telegram_id(str(message.from_user.id))
    if user:
        if user.role == 'student':
            kb = student
            await message.answer(f"Добро пожаловать, {user.role}! Вы уже зарегистрированы.", reply_markup=kb.us_main_menu_kb)
        else :
            kb = teacher
            await message.answer(f"Добро пожаловать, {user.role}! Вы уже зарегистрированы.", reply_markup=kb.us_main_menu_kb)
    else:
        await message.answer("Добро пожаловать! Вас нет в системе. Пожалуйста, свяжитесь с администратором для регистрации. @NewFail")

