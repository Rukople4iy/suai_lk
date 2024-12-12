from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import src.db.crud.teacher_crud as crud
import src.keyboards.teacher_kb as kb
from src.handlers.common_echo import require_role

router_main: Router = Router()


# Обработчик для команды "👨 Профиль" с проверкой роли учителя
@router_main.message(F.text == "👨 Профиль преподавателя")
@require_role('teacher')
async def profile_teacher(message: Message):
    teacher = crud.get_teacher_by_telegram_id(str(message.from_user.id))
    if teacher:
        profile_text = (
            f"👤 ФИО: {teacher.fio}\n"
            f"👨‍🏫 Аккаунт зарегистрирован на: {message.from_user.id}\n"
            f"🎓 Ученая степень: {teacher.academic_degree}\n"
            f"🔬 Кафедра: {teacher.department}\n"
            f"📧 Email: {teacher.email}\n"
            f"📞 Телефон: {teacher.phone}"
        )
        await message.answer(profile_text)