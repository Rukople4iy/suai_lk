from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import CommandStart
import src.db.crud.teacher_crud as crud
from datetime import datetime
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import logging

logging.basicConfig(level=logging.INFO)

router_main: Router = Router()
router_file: Router = Router()

# Хэндлер для callback_data "us_show_groups"
@router_main.callback_query(F.data == 'show_teacher_disciplines')
async def show_group_members(callback: CallbackQuery):
    await callback.answer('')
    result_list = "\n".join(crud.get_teacher_disciplines(str(callback.from_user.id)))
    message_text = f"Дисциплина | Группа\n{result_list}"

    await callback.message.answer(message_text)

class TaskForm(StatesGroup):
    discipline = State()
    groups = State()
    task_name = State()
    task_description = State()
    task_type = State()
    max_score = State()
    due_date = State()
    file_code = State()

@router_main.callback_query(F.data == 'upload_task_teacher')
async def upload_task_teacher(callback: CallbackQuery, state: FSMContext):
    # Получаем список дисциплин преподавателя
    teacher_telegram_id = callback.from_user.id
    disciplines = crud.get_teacher_disciplines(str(teacher_telegram_id))

    if not disciplines:
        await callback.message.answer("У вас нет назначенных дисциплин.")
        return

    discipline_list = "\n".join([f"{idx + 1}. {d.discipline}" for idx, d in enumerate(disciplines)])
    await callback.message.answer(f"Введите номер дисциплины\n{discipline_list}")
    await state.set_state(TaskForm.discipline)

@router_main.message()
async def process_task_steps(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == TaskForm.discipline.state:
        # Получаем выбранную дисциплину
        discipline_choice = int(message.text) - 1
        teacher_telegram_id = message.from_user.id
        disciplines = crud.get_teacher_disciplines(str(teacher_telegram_id))
        chosen_discipline = disciplines[discipline_choice].discipline

        await state.update_data(discipline=chosen_discipline)

        # Получаем список групп для выбранной дисциплины
        groups = crud.get_groups_for_discipline(chosen_discipline)
        if not groups:
            await message.answer("Нет групп для выбранной дисциплины.")
            return

        group_list = "\n".join([f"{idx + 1}. {g.group_number}" for idx, g in enumerate(groups)])
        await message.answer(f"Введите номера групп через пробел\n{group_list}")
        await state.set_state(TaskForm.groups)

    elif current_state == TaskForm.groups.state:
        group_numbers = message.text.split()
        await state.update_data(groups=group_numbers)
        await message.answer("Введите наименование задания")
        await state.set_state(TaskForm.task_name)

    elif current_state == TaskForm.task_name.state:
        await state.update_data(task_name=message.text)
        await message.answer("Введите описание задания")
        await state.set_state(TaskForm.task_description)

    elif current_state == TaskForm.task_description.state:
        await state.update_data(task_description=message.text)
        await message.answer(
            "Введите номер типа задания\n1. Лабораторная работа\n2. Индивидуальное задание\n3. Расчетно-графическая работа\n4. Курсовой проект (работа)\n5. Практические задания\n6. Отчет о научных исследованиях\n7. Эссе\n8. Реферат")
        await state.set_state(TaskForm.task_type)

    elif current_state == TaskForm.task_type.state:
        await state.update_data(task_type=message.text)
        await message.answer("Введите количество баллов задания")
        await state.set_state(TaskForm.max_score)

    elif current_state == TaskForm.max_score.state:
        await state.update_data(max_score=message.text)
        await message.answer("Введите предельную дату выполнения в формате ДД.ММ.ГГГГ")
        await state.set_state(TaskForm.due_date)

    elif current_state == TaskForm.due_date.state:
        await state.update_data(due_date=message.text)
        await message.answer("Загрузите дополнительный материал (максимум 1 файл)")
        await state.set_state(TaskForm.file_code)

@router_file.message(F.content_type == ContentType.DOCUMENT)
async def process_file_code(message: Message, state: FSMContext):
    current_state = await state.get_state()
    logging.info("получили состояние")
    if current_state == TaskForm.file_code.state:
        logging.info("Файл получен.")
        file_code = message.document.file_id
        logging.info("получен id файла.")
        await state.update_data(file_code=file_code)
        logging.info("Файл id сохранен в состояние.")
        await message.answer("Готово. Задание сформировано и будет отправлено в базу данных.")

        # Retrieve data from state and send to database
        async with state.proxy() as data:
            create_task_for_teacher(
                discipline=data['discipline'],
                group_numbers=data['groups'],
                task_name=data['task_name'],
                task_description=data['task_description'],
                task_type=data['task_type'],
                max_score=data['max_score'],
                due_date=data['due_date'],
                file_code=data['file_code']
            )
        logging.info("попытка сохранения в базу")
        await state.finish()

