from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import src.db.crud as crud
import src.keyboards.kb as kb

router_main: Router = Router()

class AuthState(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

# Хэндлер для команды /start
@router_main.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    student = crud.get_student_by_telegram_id(str(message.from_user.id))
    if student:
        await message.answer(f"Добро пожаловать, {student.login}! Вы уже зарегистрированы.", reply_markup=kb.us_main_menu_kb)
    else:
        await message.answer("Добро пожаловать! Вас нет в системе. Нажмите кнопку ниже для входа в аккаунт.", reply_markup=kb.hello_kb)

# Хэндлер для callback_data "sign_in"
@router_main.callback_query(F.data == 'sign_in')
async def sign_in_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.edit_text("Введите ваш логин:")
    await state.set_state(AuthState.waiting_for_login)

# Обработчик ввода логина
@router_main.message(AuthState.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    login = message.text
    await state.update_data(login=login)
    await message.answer("Теперь введите ваш пароль:")
    await state.set_state(AuthState.waiting_for_password)

# Обработчик ввода пароля
@router_main.message(AuthState.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    student_data = await state.get_data()
    login = student_data.get('login')
    password = message.text.strip()

    student = crud.validate_student_login(login, password)
    if student:
        if not student.telegram_id:
            crud.update_student_telegram_id(login, str(message.from_user.id))
        await message.answer(f"Вы вошли как {student.login}.", reply_markup=kb.us_main_menu_kb)
        await state.clear()
    else:
        await message.answer("Неверный логин или пароль. Попробуйте снова.")
        await state.clear()

# Хэндлер для повторной попытки входа
@router_main.callback_query(F.data == 'retry_sign')
async def retry_sign_in_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.answer("Введите ваш логин:")
    await state.set_state(AuthState.waiting_for_login)

# Хэндлер для связи с техподдержкой
@router_main.callback_query(F.data == 'contact_support')
async def contact_support_cb(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer("Пожалуйста, свяжитесь с админом: @NewFail")

# Проверка авторизации для всех хэндлеров, связанных с пользователем
def require_login(handler):
    async def wrapper(message_or_callback, *args, **kwargs):
        # Удаляем все неожиданные именованные аргументы
        accepted_args = handler.__code__.co_varnames[:handler.__code__.co_argcount]
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in accepted_args}

        student = crud.get_student_by_telegram_id(str(message_or_callback.from_user.id))
        if not student:
            if isinstance(message_or_callback, Message):
                await message_or_callback.answer("Вы не авторизованы. Пожалуйста, войдите в систему с помощью команды /start")
            else:
                await message_or_callback.answer("Вы не авторизованы. Пожалуйста, войдите в систему с помощью команды /start")
            return
        await handler(message_or_callback, *args, **filtered_kwargs)
    return wrapper

# Хэндлер для кнопки "Профиль"
@router_main.message(F.text == "👨 Профиль")
@require_login
async def profile(message: Message):
    student = crud.get_student_by_telegram_id(str(message.from_user.id))
    profile_text = (
        f"👤 ФИО: {student.fio}\n"
        f"👨‍🏫 Аккаунт зарегистрирован на: @{message.from_user.username}\n"
        f"🏫 Институт/факультет: {student.group.institute}\n"
        f"👥 Группа: {student.group.group_number}\n"
        f"📃 Номер студенческого билета/зачетной книжки: {student.student_id}\n"
        f"👨‍🔬 Специальность: {student.group.specialty}\n"
        f"👀 Форма обучения: {student.group.form_of_study}\n"
        f"🎓 Уровень профессионального образования: {student.group.education_level}\n"
        f"🤑 Бюджет/контракт: {student.budget_contract}"
    )
    await message.answer(profile_text)

# Хэндлер для кнопки "Информация"
@router_main.message(F.text == "💁‍♂️ Информация")
@require_login
async def info(message: Message):
    info_text = "Выберите интересующую вас информацию:"
    await message.answer(info_text, reply_markup=kb.us_info_kb)

# Хэндлер для callback_data "us_show_groups"
@router_main.callback_query(F.data == 'us_show_groups')
@require_login
async def show_group_members(callback: CallbackQuery):
    await callback.answer('')
    student = crud.get_student_by_telegram_id(str(callback.from_user.id))
    group_members = crud.get_students_by_group_number(student.group_number)
    if group_members:
        members_list = "\n".join([f"{index + 1}. {member.fio} (@{member.login})" for index, member in enumerate(group_members)])
        await callback.message.answer(f"👥 Список участников группы {student.group.group_number}:\n{members_list}")
    else:
        await callback.message.answer("В вашей группе пока нет других участников.")

# Хэндлер для кнопки "Связаться с админом"
@router_main.message(F.text == "👩‍💻 Связаться с админом")
@require_login
async def contact_admin(message: Message):
    admins_list = "Админы: @NewFail, @Rukople4iy, @ma_lh"
    await message.answer(admins_list)
