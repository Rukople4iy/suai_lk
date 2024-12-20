# клавы
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


main_menu_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👨 Профиль"), KeyboardButton(text="🧐 Задания")],
    [KeyboardButton(text="💁‍♂️ Информация")],
    [KeyboardButton(text="❓ Как все работает"), KeyboardButton(text="👩‍💻 Связаться с админом")]
], resize_keyboard=True, input_field_placeholder="Выберите пункт меню")

info_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📚 Дисциплины", callback_data="show_disciplines_and_teachers")],
    [InlineKeyboardButton(text="📝 Группа", callback_data="show_group_members")]
])

task_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👀 Посмотреть задания", callback_data="browse_task")],
])

task_view_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✏ Просмотреть задание", callback_data="view_task")],
    [InlineKeyboardButton(text="📝 Загрузить отчет", callback_data="upload_report")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_task")]
])


def generate_task_view_kb(task_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏ Просмотреть задание", callback_data=f"file_task:{task_id}")],
        [InlineKeyboardButton(text="📝 Загрузить отчет", callback_data=f"upload_report:{task_id}")]
    ])
