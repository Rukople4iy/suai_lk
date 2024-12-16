# клавы
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

hello_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔐 Войти в аккаунт", callback_data="sign_in")]
])

retry_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="retry_sign")],
    [InlineKeyboardButton(text="📞 Связаться с техподдержкой", callback_data="contact_support")]
])

main_menu_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👨 Профиль"), KeyboardButton(text="🧐 Задания")],
    [KeyboardButton(text="👥 Материалы"), KeyboardButton(text="📊 Объявления")],
    [KeyboardButton(text="💁‍♂️ Информация")],
    [KeyboardButton(text="❓ Как все работает"), KeyboardButton(text="👩‍💻 Связаться с админом")]
], resize_keyboard=True, input_field_placeholder="Выберите пункт меню")

info_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📚 Дисциплины", callback_data="show_disciplines_and_teachers")],
    [InlineKeyboardButton(text="📝 Группа", callback_data="show_group_members")]
])

task_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📩 Загрузка заданий", callback_data="upload_task")],
    [InlineKeyboardButton(text="✅ Проверка заданий", callback_data="check_task")]
])
