# клавы
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


main_menu_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👨 Профиль"), KeyboardButton(text="🧐 Задания")],
    [KeyboardButton(text="️📚 Информация")],
    [KeyboardButton(text="❓ Как все работает"), KeyboardButton(text="👨‍💻 Связаться с админом")]
], resize_keyboard=True, input_field_placeholder="Выберите пункт меню")

info_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📚 Дисциплины", callback_data="show_teacher_disciplines")]
])

#Загрузить и проверить задание
task_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📩 Загрузка заданий", callback_data="upload_task_teacher")],
    [InlineKeyboardButton(text="✅ Проверка заданий", callback_data="check_task_teacher")]
])

def generate_teacher_report_kb(report_id, ischecked):
    if ischecked:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏ Просмотреть отчет", callback_data=f"view_report:{report_id}")],
            [InlineKeyboardButton(text="👥 Назад к списку студентов", callback_data="back_to_students")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏ Просмотреть отчет", callback_data=f"view_report:{report_id}")],
            [InlineKeyboardButton(text="📝 Оценить выполнение", callback_data=f"estimate_report:{report_id}")],
            [InlineKeyboardButton(text="👥 Назад к списку студентов", callback_data="back_to_students")]
        ])

approve_report_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Подтвердить", callback_data="approve_report")],
    [InlineKeyboardButton(text="❌ Отклонить", callback_data="reject_report")]
])

#Вернуться в главное меню
choose_student_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📃 Назад к списку заданий", callback_data="back_to_tasks_teacher")],
    [InlineKeyboardButton(text="🔙 Вернуться в главное меню", callback_data="back_to_main_menu_teacher")]
])

back_to_main_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Отменить и вернуться в главное меню", callback_data="back_to_main_menu_teacher")]
])