from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import src.db.crud.student_crud as crud
import src.keyboards.student_kb as kb

import logging


logging.basicConfig(level=logging.INFO)
router_main: Router = Router()

# состояния просмотрв заданий

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




class CheckTask(StatesGroup):
    discipline = State()
    task_id = State()
    task_view = State()

# просмотреть задания
@router_main.callback_query(F.data == 'browse_task')
async def browse_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    disciplines = crud.get_student_disciplines(str(callback.from_user.id))
    result_list = "\n".join(f"{i + 1}. {d}" for i, d in enumerate(disciplines))
    message_text = f"Выберите дисциплину, введя её номер:\n{result_list}"

    await callback.message.answer(message_text)
    await state.update_data(disciplines=disciplines)
    await state.set_state(CheckTask.discipline)

# ожидание выбора номера дисциплины
@router_main.message(CheckTask.discipline)
async def select_discipline(message: Message, state: FSMContext):
    state_data = await state.get_data()
    disciplines = state_data.get('disciplines')
    selected_number = int(message.text.strip()) - 1

    if 0 <= selected_number < len(disciplines):
        selected_discipline = disciplines[selected_number]
        await state.update_data(selected_discipline=selected_discipline)
        tasks = crud.get_student_tasks(selected_discipline, str(message.from_user.id))
        result_list = "\n".join(f"{i + 1}.  ❕{d.task_type}\n🔎{d.task_name}\n⏳Сдать до {d.due_date}\n" for i, d in enumerate(tasks))
        message_text = f"Вы выбрали дисциплину: {selected_discipline}\nВыберите задание, введя его номер:\n{result_list}"

        await state.update_data(tasks=tasks, selected_discipline=selected_discipline)
        await message.answer(message_text)
        await state.set_state(CheckTask.task_view)
    else:
        await message.answer("Некорректный номер. Пожалуйста, выберите правильный номер дисциплины.")

# ожидание выбора задания, вывод информации о задании
@router_main.message(CheckTask.task_view)
async def select_task(message: Message, state: FSMContext):
    state_data = await state.get_data()
    tasks = state_data.get('tasks')
    selected_number = int(message.text.strip()) - 1

    if 0 <= selected_number < len(tasks):
        selected_task = tasks[selected_number]
        await state.update_data(task=selected_task)

        message_text = f"Вы выбрали задание:\n{selected_task.task_type}\n{selected_task.task_name}\n{selected_task.task_description}\nСдать до {selected_task.due_date}"
        await message.answer(message_text, reply_markup=kb.generate_task_view_kb(selected_task.task_id))
        await state.clear()
    else:
        await message.answer("Некорректный номер. Пожалуйста, выберите правильный номер задания.")


class LoadReport(StatesGroup):
    process_file = State()




# получить задание из базы данных
@router_main.callback_query(F.data.startswith('file_task:'))
async def browse_task(callback: CallbackQuery):
    selected_task_id = callback.data.split(':')[1]
    await callback.answer('')
    file = crud.get_file_code(selected_task_id)
    await callback.message.answer_document(file)

@router_main.callback_query(F.data.startswith('upload_report:'))
async def upload_report(callback: CallbackQuery, state: FSMContext):
    selected_task_id = callback.data.split(':')[1]
    await callback.answer('')
    await state.set_state(LoadReport.process_file)
    await state.update_data(selected_task_id=selected_task_id)
    await callback.message.answer("Загрузите отчет (максимум 1 файл)")

async def handle_load_report_file(message: Message, state: FSMContext):
    logging.info("Файл получен для LoadReport.")
    state_data = await state.get_data()
    selected_task_id = state_data.get("selected_task_id")
    file_code = message.document.file_id
    logging.info("получен id файла.")
    await message.answer("Готово. Отчет сформирован и будет отправлен в базу данных.")

    try:
        crud.add_report(selected_task_id, str(message.from_user.id), file_code)
        logging.info("Отчет успешно сохранен в базу данных.")
    except Exception as e:
        logging.error(f"Ошибка при сохранении отчета: {e}")
        await message.answer("Произошла ошибка при сохранении отчета. Попробуйте снова.")

    await state.clear()