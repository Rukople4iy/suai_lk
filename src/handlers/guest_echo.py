from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import src.handlers.student_echo as student_echo
import src.handlers.teacher_echo as teacher_echo
import src.handlers.admin_echo as admin_echo
import src.db.crud.common_crud as crud
import src.keyboards.student_kb as student
import src.keyboards.teacher_kb as teacher
from src.handlers.common_echo import get_role
import logging

logging.basicConfig(level=logging.INFO)

router_main: Router = Router()

# Хэндлер для команды /start
@router_main.message(CommandStart())
async def send_welcome(message: Message):
    role = get_role(str(message.from_user.id))
    if role:
        if role == 'student':
            kb = student
            await message.answer(f"Добро пожаловать, {user.role}! Вы уже зарегистрированы.", reply_markup=kb.main_menu_kb)
        else :
            kb = teacher
            await message.answer(f"Добро пожаловать, {user.role}! Вы уже зарегистрированы.", reply_markup=kb.main_menu_kb)
    else:
        await message.answer("Добро пожаловать! Вас нет в системе. Пожалуйста, свяжитесь с администратором для регистрации. @NewFail")

