import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

API_TOKEN = 'YOUR_API_TOKEN'  # Убедитесь, что здесь ваш токен

# Подключение к базе данных
conn = sqlite3.connect('instance/bot_database.db')
cursor = conn.cursor()

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Хэндлер для команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Добро пожаловать! Для входа используйте команду /login.")

# Хэндлер для команды /login
@dp.message(Command("login"))
async def login(message: Message):
    await message.answer("Введите ваши логин и пароль в формате: /login login password")

# Обработчик сообщений для ввода логина и пароля
@dp.message(Command("login"))
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

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())