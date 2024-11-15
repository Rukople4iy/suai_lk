from aiogram import Router #F
from aiogram.types import Message #CallbackQuery
from aiogram.filters import CommandStart
#from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
#from src.db.db import db_context
import src.keyboards.kb as kb

router_main: Router = Router()


class StateRegisterLogin(StatesGroup):
    waiting_for_reg_data = State()


@router_main.message(CommandStart())
async def start_handler(message: Message):
    #db = db_context.get()
    #user_added = await db.add_user(str(message.from_user.id))
    if user_added:
        await message.reply("Вы успешно зарегистрированы! Теперь у вас есть доступ к платформе.",
                            reply_markup=kb.main_menu_kb)
    else:
        await message.reply("Вы уже зарегистрированы! Теперь у вас есть доступ к платформе.",
                            reply_markup=kb.main_menu_kb



# Хэндлер для команды /start
@router_main.message(CommandStart)
async def send_welcome(message: Message):
    await message.answer("Добро пожаловать! Вас нет в системе", reply_markup=kb.hello_kb)

# Хэндлер для команды /login
@router_main.message(Command("login"))
async def login(message: Message):
    await message.answer("Введите ваши логин и пароль в формате: /login login password")

# Обработчик сообщений для ввода логина и пароля
@router_main.message(Command("login"))
async def handle_login(message: Message):
    try:
        # Разделение введённого текста на части
        _, login, password = message.text.split()  # Разделяет сообщение на части по пробелам
        cursor.execute("SELECT id, role FROM users WHERE login = ? AND password = ?", (login, password))
        user = cursor.fetchone()
        if user:
            await message.answer(f"Вы вошли как {user[1]}.")
        else:
            await message.answer("Неверный логин или пароль.")
    except ValueError:
        await message.answer("Неправильный формат команды. Используйте: /login login password.")
