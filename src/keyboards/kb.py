# клавы
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

hello_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔐 Войти в аккаунт", callback_data="sign_in")]
])

main_menu_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👨 Личный кабинет"),KeyboardButton(text="🧐 Задания" )],
    [KeyboardButton(text="👥 Группа"),KeyboardButton(text="📊 Расписание" )],
    [KeyboardButton(text="❓ Как все работает"),KeyboardButton(text="👩‍💻 Связаться с админом")]
],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню")