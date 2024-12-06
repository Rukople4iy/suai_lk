from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.db.db import get_user_by_telegram_id, validate_user_login, update_telegram_id, get_users_by_group_id
import src.keyboards.kb as kb

router_main: Router = Router()

class AuthState(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

# Хэндлер для команды /start
@router_main.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    user = get_user_by_telegram_id(str(message.from_user.id))
    if user:
        await message.answer(f"Добро пожаловать, {user.login}! Вы уже зарегистрированы.", reply_markup=kb.us_main_menu_kb)
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
    user_data = await state.get_data()
    login = user_data.get('login')
    password = message.text.strip()

    user = validate_user_login(login, password)
    if user:
        if not user.telegram_id:
            update_telegram_id(login, str(message.from_user.id))
        await message.answer(f"Вы вошли как {user.login}.", reply_markup=kb.us_main_menu_kb)
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
    await callback.message.answer("Пожалуйста, свяжитесь с техподдержкой по email: support@example.com.")

# Проверка авторизации для всех хэндлеров, связанных с пользователем
def require_login(handler):
    async def wrapper(message_or_callback, *args, **kwargs):
        user = get_user_by_telegram_id(str(message_or_callback.from_user.id))
        if not user:
            if isinstance(message_or_callback, Message):
                await message_or_callback.answer("Вы не авторизованы. Пожалуйста, войдите в систему./start")
            else:
                await message_or_callback.answer("Вы не авторизованы. Пожалуйста, войдите в систему./start")
            return
        await handler(message_or_callback, *args, **kwargs)
    return wrapper

# Хэндлер для кнопки "Профиль"
@router_main.message(F.text == "👨 Профиль")
@require_login
async def profile(message: Message):
    user = get_user_by_telegram_id(str(message.from_user.id))
    profile_text = (
        f"👤 ФИО: {user.fio}\n"
        f"👨‍🏫 Аккаунт зарегестрирован на: @{message.from_user.username}\n"
        f"🏫 Институт/факультет: {user.institute}\n"
        f"👥 Группа: {user.group.name}\n"
        f"📃 Номер студенческого билета/ зачетной книжки: {user.student_id}\n"
        f"👨‍🔬 Специальность: {user.specialty}\n"
        f"👀 Форма обучения: {user.form_of_study}\n"
        f"🎓 Уровень профессионального образования: {user.education_level}\n"
        f"🤑 Бюджет/контракт: {user.budget_contract}"
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
    user = get_user_by_telegram_id(str(callback.from_user.id))
    group_members = get_users_by_group_id(user.group_id)
    if group_members:
        members_list = "\n".join([f"{index + 1}. {member.fio} (@{member.login})" for index, member in enumerate(group_members)])
        await callback.message.answer(f"👥 Список участников группы {user.group.name}:\n{members_list}")
    else:
        await callback.message.answer("В вашей группе пока нет других участников.")

# Хэндлер для кнопки "Связаться с админом"
@router_main.message(F.text == "👩‍💻 Связаться с админом")
@require_login
async def contact_admin(message: Message):
    admins_list = "Админы: @NewFail, @Rukople4iy, @ma_lh"
    await message.answer(admins_list)
