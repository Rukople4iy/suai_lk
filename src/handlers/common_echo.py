from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from functools import wraps
from aiogram.types import Message
import src.db.crud.common_crud as common_crud
import logging
import src.db.crud.teacher_crud as teacher_crud
import src.keyboards.teacher_kb as teacher_kb
import src.db.crud.student_crud as student_crud
import src.keyboards.student_kb as  student_kb

logging.basicConfig(level=logging.INFO)

router_main: Router = Router()

#Функция для проверки роли, возвращает роль
def get_role(telegram_id):
    user = common_crud.get_user_by_telegram_id(telegram_id)
    return user.role


def require_role(role):
    def decorator(handler):
        async def wrapper(message_or_callback, *args, **kwargs):
            accepted_args = handler.__code__.co_varnames[:handler.__code__.co_argcount]
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in accepted_args}

            user_role = get_role(str(message_or_callback.from_user.id))

            if not user_role or user_role != role:
                await message_or_callback.answer("У вас нет прав для выполнения этого действия.")
                return
            await handler(message_or_callback, *args, **filtered_kwargs)
        return wrapper
    return decorator

@router_main.message(F.text == "👨 Профиль")
async def profile(message: Message):
    role = get_role(str(message.from_user.id))
    if role == 'student':
        student = student_crud.get_student_by_telegram_id(str(message.from_user.id))
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
    elif role == 'teacher':
        teacher = teacher_crud.get_teacher_by_telegram_id(str(message.from_user.id))
        if teacher:
            profile_text = (
                    f"👤 ФИО: {teacher.fio}\n"
                    f"👨‍🏫 Аккаунт зарегистрирован на: {message.from_user.username}\n"
                    f"🎓 Ученая степень: {teacher.academic_degree}\n"
                    f"🔬 Кафедра: {teacher.department}\n"
                    f"📧 Email: {teacher.email}\n"
                    f"📞 Телефон: {teacher.phone}"
                )
            await message.answer(profile_text)

#Кнопка информация (вывод двух кнопок)
@router_main.message(F.text == "💁‍♂️ Информация")
async def information(message: Message):
    role = get_role(str(message.from_user.id))
    if role == 'student':
        kb = student_kb
        await message.answer("Выберите категорию", reply_markup=kb.info_kb)
    elif role == 'teacher':
        kb = teacher_kb
        await message.answer("Выберите категорию", reply_markup=kb.info_kb)


#Кнопка информация (вывод двух кнопок)
@router_main.message(F.text == "💁‍♂️ Информация")
async def task(message: Message):
    role = get_role(str(message.from_user.id))
    if role == 'student':
        kb = student_kb
        await message.answer("Выберите категорию", reply_markup=kb.task_kb)
    elif role == 'teacher':
        kb = teacher_kb
        await message.answer("Выберите категорию", reply_markup=kb.task_kb)