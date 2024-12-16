from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import src.db.crud.student_crud as crud
import src.keyboards.student_kb as kb
from src.handlers.common_echo import require_role

router_main: Router = Router()

@router_main.callback_query(F.data == 'show_disciplines_and_teachers')
async def show_disciplines_and_teachers(callback: CallbackQuery):
    await callback.answer('')
    result_list = "\n".join(crud.get_disciplines_and_teachers(str(callback.from_user.id)))
    message_text = f"Дисциплина | Преподаватели\n{result_list}"

    await callback.message.answer(message_text)

@router_main.callback_query(F.data == 'show_group_members')
async def show_group_members(callback: CallbackQuery):
    await callback.answer('')
    group_number = (crud.get_student_by_telegram_id(str(callback.from_user.id))).group_number
    result_list = "\n".join(crud.get_group_members(str(callback.from_user.id)))
    message_text = f"Список группы {group_number}:\n{result_list}"

    await callback.message.answer(message_text)