from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from functools import wraps
from aiogram.types import Message
import src.db.crud.common_crud as common_crud
import logging
import src.db.crud.teacher_crud as teacher_crud
import src.keyboards.teacher_kb as teacher_kb
import src.db.crud.student_crud as student_crud
import src.keyboards.student_kb as student_kb
import src.keyboards.kb as common_kb
from src.handlers.student_echo import CheckTask, handle_load_report_file
from src.handlers.teacher_echo import TaskForm,  handle_task_form_file



logging.basicConfig(level=logging.INFO)

router_main: Router = Router()
router_file: Router = Router()

def require_role(role):
    def decorator(handler):
        async def wrapper(message_or_callback, *args, **kwargs):
            accepted_args = handler.__code__.co_varnames[:handler.__code__.co_argcount]
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in accepted_args}

            user_role = common_crud.get_role_by_telegram_id(str(message_or_callback.from_user.id))

            if not user_role or user_role != role:
                await message_or_callback.answer("У вас нет прав для выполнения этого действия.")
                return
            await handler(message_or_callback, *args, **filtered_kwargs)
        return wrapper
    return decorator

@router_main.message(F.text == "👨 Профиль")
async def profile(message: Message):
    role = common_crud.get_role_by_telegram_id(str(message.from_user.id))
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
    role = common_crud.get_role_by_telegram_id(str(message.from_user.id))
    if role == 'student':
        kb = student_kb
        await message.answer("Выберите категорию", reply_markup=kb.info_kb)
    elif role == 'teacher':
        kb = teacher_kb
        await message.answer("Выберите категорию", reply_markup=kb.info_kb)


#Кнопка информация (вывод двух кнопок)
@router_main.message(F.text == "🧐 Задания")
async def task(message: Message):
    role = common_crud.get_role_by_telegram_id(str(message.from_user.id))
    if role == 'student':
        kb = student_kb
        await message.answer("Выберите категорию", reply_markup=kb.task_kb)
    elif role == 'teacher':
        kb = teacher_kb
        await message.answer("Выберите категорию", reply_markup=kb.task_kb)

@router_main.message(F.text == "👩‍💻 Связаться с админом")
async def contact_admin(message: Message):
    await message.answer("😍Наши админы", reply_markup=common_kb.contacts_kb)

@router_main.message(F.text == "❓ Как все работает")
async def how_to_use(message: Message):
    role = common_crud.get_role_by_telegram_id(str(message.from_user.id))
    if role == 'teacher':
        message_text = """
Кнопка “Профиль” – информация о Вас
Кнопка “Задания” – загрузка заданий и проверка заданий
Кнопка “Информация” – кнопки “Дисциплина” и “Группа” для получения сведений о доступных дисциплинах и привязанных групп
Кнопка “Связаться с админом” – кнопки для перехода к чатам с администраторами
        """
        await message.answer(message_text)
    elif role == 'student':
        message_text = """
Кнопка “Профиль” – информация о Вас
Кнопка “Задания” – загрузка отчётов
Кнопка “Информация” – кнопки “Дисциплина” для доступа к сведениям о привязанных дисциплинах
Кнопка “Связаться с админом” – кнопки для перехода к чатам с администраторами
                """
        await message.answer(message_text)


@router_file.message(F.content_type == ContentType.DOCUMENT)
async def process_file_code(message: Message, state: FSMContext):
    logging.info("увидели файл и вошли в состояние.")
    current_state = await state.get_state()
    logging.info(f"получили состояние: {current_state}")


    if current_state == TaskForm.file_code.state:
        await handle_task_form_file(message, state)
    elif current_state == CheckTask.process_file.state:
        await handle_load_report_file(message, state)
