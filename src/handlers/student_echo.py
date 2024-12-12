from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import src.db.crud.student_crud as crud
import src.keyboards.student_kb as kb
from src.handlers.common_echo import require_role

router_main: Router = Router()


# Обработчик для команды "👨 Профиль" с проверкой роли студента
@router_main.message(F.text == "👨 Профиль студента")
@require_role('student')
async def profile_student(message: Message):
    student = crud.get_student_by_telegram_id(str(message.from_user.id))
    if student:
        profile_text = (
            f"👤 ФИО: {student.fio}\n"
            f"👨‍🏫 Аккаунт зарегистрирован на: @{message.from_user.username}\n"
            f"🏫 Институт/факультет: {student.group.institute}\n"
            f"👥 Группа: {student.group.group_number}\n"
            f"👨‍🔬 Специальность: {student.group.specialty}\n"
            f"👀 Форма обучения: {student.group.form_of_study}\n"
            f"🎓 Уровень профессионального образования: {student.group.education_level}\n"
            f"🤑 Бюджет/контракт: {student.budget_contract}"
        )
        await message.answer(profile_text)