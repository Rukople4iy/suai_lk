from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import src.db.crud.teacher_crud as crud
import src.keyboards.teacher_kb as kb
from src.handlers.common_echo import require_role

router_main: Router = Router()


# Хэндлер для callback_data "us_show_groups"
@router_main.callback_query(F.data == 'show_teacher_disciplines')
async def show_group_members(callback: CallbackQuery):
    await callback.answer('')
    result_list = "\n".join(crud.get_teacher_disciplines(str(callback.from_user.id)))
    message_text = f"Дисциплина | Группа\n{result_list}"

    await callback.message.answer(message_text)
