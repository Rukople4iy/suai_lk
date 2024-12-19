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

us_main_menu_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👨 Профиль"), KeyboardButton(text="🧐 Задания")],
    [KeyboardButton(text="👥 Материалы"), KeyboardButton(text="📊 Объявления")],
    [KeyboardButton(text="💁‍♂️ Информация")],
    [KeyboardButton(text="❓ Как все работает"), KeyboardButton(text="👩‍💻 Связаться с админом")]
], resize_keyboard=True, input_field_placeholder="Выберите пункт меню")

us_info_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📚 Дисциплины", callback_data="us_show_disciplines")],
    [InlineKeyboardButton(text="📝 Группа", callback_data="us_show_groups")]
])


contacts_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📞Андрон", url="https://t.me/newfail")],
    [InlineKeyboardButton(text="🤠Лёха", url="https://t.me/Rukople4iy")]
])
