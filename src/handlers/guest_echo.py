from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import src.handlers.student_echo as student_echo
import src.handlers.teacher_echo as teacher_echo
import src.db.crud.common_crud as crud
import src.db.crud.student_crud as student_crud
import src.db.crud.teacher_crud as teacher_crud
import src.keyboards.student_kb as student_kb
import src.keyboards.teacher_kb as teacher_kb
import logging

logging.basicConfig(level=logging.INFO)

router_main: Router = Router()

# Хэндлер для команды /start
@router_main.message(CommandStart())
async def send_welcome(message: Message):
    role = crud.get_role_by_telegram_id(str(message.from_user.id))
    if role:
        if role == 'student':
            kb = student_kb
            student = student_crud.get_student_by_telegram_id(str(message.from_user.id))
            await message.answer(f"Добро пожаловать, {student.fio}! Вы уже зарегистрированы.", reply_markup=kb.main_menu_kb)
        else :
            kb = teacher_kb
            teacher = teacher_crud.get_teacher_by_telegram_id(str(message.from_user.id))
            await message.answer(f"Добро пожаловать, {teacher.fio}! Вы уже зарегистрированы.", reply_markup=kb.main_menu_kb)
    else:
        await message.answer("Добро пожаловать! Вас нет в системе. Пожалуйста, свяжитесь с администратором для регистрации. @NewFail")

