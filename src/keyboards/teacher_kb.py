# клавы
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


main_menu_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👨 Профиль"), KeyboardButton(text="🧐 Задания")],
    [KeyboardButton(text="💁‍♂️ Информация")],
    [KeyboardButton(text="❓ Как все работает"), KeyboardButton(text="👩‍💻 Связаться с админом")]
], resize_keyboard=True, input_field_placeholder="Выберите пункт меню")

info_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📚 Дисциплины", callback_data="show_teacher_disciplines")]
])

#Загрузить и проверить задание
task_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📩 Загрузка заданий", callback_data="upload_task_teacher")],
    [InlineKeyboardButton(text="✅ Проверка заданий", callback_data="check_task_teacher")]
])