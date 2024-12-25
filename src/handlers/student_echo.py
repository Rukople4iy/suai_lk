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
    data = crud.get_disciplines_and_teachers(str(callback.from_user.id))

    if not data or isinstance(data, str):  # Если данные отсутствуют или это сообщение об ошибке
        await callback.message.answer(data if isinstance(data, str) else "Нет данных о дисциплинах и преподавателях.")
        return

    # Формируем список
    message_text = "*Дисциплины и преподаватели:*\n\n" + "\n".join(
        f"📚 {entry.split(' | ')[0]}\n👨‍🏫 {entry.split(' | ')[1]} \n" for entry in data
    )

    # Отправляем сообщение
    await callback.message.answer(message_text, parse_mode="Markdown")


@router_main.callback_query(F.data == 'show_group_members')
async def show_group_members(callback: CallbackQuery):
    await callback.answer('')
    student = crud.get_student_by_telegram_id(str(callback.from_user.id))

    if not student:
        await callback.message.answer("Студент не найден.")
        return

    group_number = student.group_number
    group_members = crud.get_group_members(str(callback.from_user.id))

    if isinstance(group_members, str):  # Если вернулось сообщение об ошибке
        await callback.message.answer(group_members)
        return

    # Формируем список студентов с табуляцией
    result_list = "\n".join(f"\t{member}" for member in group_members)
    message_text = f"👥*Список группы {group_number}:*\n\n{result_list}"

    await callback.message.answer(message_text, parse_mode="Markdown")






class CheckTask(StatesGroup):
    discipline = State()
    task_id = State()
    task_view = State()
    process_file = State()
    idle = State()

# просмотреть задания
@router_main.callback_query(F.data == 'browse_task')
async def browse_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    disciplines = crud.get_student_disciplines(str(callback.from_user.id))
    result_list = "\n".join(f"{i + 1}. {d}" for i, d in enumerate(disciplines))
    message_text = f"Выберите дисциплину, введя её номер:\n{result_list}"

    await callback.message.answer(message_text, reply_markup=kb.back_to_main_menu_kb)
    await state.update_data(disciplines=disciplines)
    await state.set_state(CheckTask.discipline)

# ожидание выбора номера дисциплины
@router_main.message(CheckTask.discipline)
async def select_discipline(message: Message, state: FSMContext):
    state_data = await state.get_data()
    disciplines = state_data.get('disciplines')
    selected_number = int(message.text.strip()) - 1
    await state.update_data(message_tasks=message)
    if 0 <= selected_number < len(disciplines):
        selected_discipline = disciplines[selected_number]
        await state.update_data(selected_discipline=selected_discipline)
        tasks = crud.get_student_tasks(selected_discipline, str(message.from_user.id))
        result_list = "\n".join(f"{i + 1}.  ❕{d.task_type}\n🔎{d.task_name}\n⏳Сдать до {d.due_date}\n" for i, d in enumerate(tasks))
        message_text = f"Вы выбрали дисциплину: {selected_discipline}\nВыберите задание, введя его номер:\n{result_list}"

        await state.update_data(tasks=tasks, selected_discipline=selected_discipline)
        await message.answer(message_text, reply_markup=kb.back_to_main_menu_kb)
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
        report = crud.get_report(selected_task.task_id)

        if report is None:
            message_text = (f"Вы выбрали задание:\n{selected_task.task_type}\n{selected_task.task_name}\n"
                            f"{selected_task.task_description}\nСдать до {selected_task.due_date}\n"
                            f"\nВы еще не сдали отчет")
            await message.answer(message_text, reply_markup=kb.generate_task_view_kb(selected_task.task_id, status="not_sent", report_id=None))
        elif report["report_status"] == "Отправлено":
            message_text = (f"Вы выбрали задание:\n{selected_task.task_type}\n{selected_task.task_name}\n"
                            f"{selected_task.task_description}\nСдать до {selected_task.due_date}\n"
                            f"\nВы сдали отчет, но его еще не проверили\nСдано: {report['upload_date']}")
            await message.answer(message_text, reply_markup=kb.generate_task_view_kb(selected_task.task_id, status="sent", report_id=report['report_id']))
        elif report["report_status"] == "Проверено":
            message_text = (f"Вы выбрали задание:\n{selected_task.task_type}\n{selected_task.task_name}\n"
                            f"{selected_task.task_description}\nСдать до {selected_task.due_date}\n"
                            f"\nВы сдали отчет и его проверили:\nСдано: {report['upload_date']}\n"
                            f"Оценка: {report['score']}/{report['max_score']}\nКомментарий преподавателя: {report['teacher_comment']}")
            await message.answer(message_text, reply_markup=kb.generate_task_view_kb(selected_task.task_id, status="checked", report_id=report['report_id']))
        else:
            message_text = (f"Вы выбрали задание:\n{selected_task.task_type}\n{selected_task.task_name}\n"
                            f"{selected_task.task_description}\nСдать до {selected_task.due_date}\n"
                            f"\nВы еще не сдали отчет")
            await message.answer(message_text, reply_markup=kb.generate_task_view_kb(selected_task.task_id, status="not_sent", report_id=None))

        await state.set_state(CheckTask.idle)
    else:
        await message.answer("Некорректный номер. Пожалуйста, выберите правильный номер задания.")



@router_main.callback_query(F.data.startswith('view_self_report:'))
async def view_report(callback: CallbackQuery):
    selected_report_id = callback.data.split(':')[1]
    await callback.answer('')
    file = crud.get_file_code_for_report(selected_report_id)
    await callback.message.answer_document(file)

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
    await state.set_state(CheckTask.process_file)
    await state.update_data(selected_task_id=selected_task_id)
    await callback.message.answer("Загрузите отчет (максимум 1 файл)", reply_markup=kb.back_to_task_kb)

async def handle_load_report_file(message: Message, state: FSMContext):
    logging.info("Файл получен для LoadReport.")
    state_data = await state.get_data()
    selected_task_id = state_data.get("selected_task_id")
    file_code = message.document.file_id
    logging.info("получен id файла.")
    await message.answer("Готово. Отчет сформирован и будет отправлен в базу данных.", reply_markup=kb.main_menu_kb)

    try:
        crud.add_report(selected_task_id, str(message.from_user.id), file_code)
        logging.info("Отчет успешно сохранен в базу данных.")
    except Exception as e:
        logging.error(f"Ошибка при сохранении отчета: {e}")
        await message.answer("Произошла ошибка при сохранении отчета. Попробуйте снова.")

    await state.clear()


# callback back_to_tasks отменить отправку отчета и вернуться к  функции select_discipline c параметрами message_tasks(из состояния) и state
@router_main.callback_query(F.data == 'back_to_tasks')
async def back_to_tasks(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    message_tasks = state_data.get('message_tasks')
    await state.set_state(CheckTask.discipline)
    await callback.answer('')
    await select_discipline(message_tasks, state)


# функция callback back_to_main_menu для возврата в главное меню отменящее текущее состояние
@router_main.callback_query(F.data == 'back_to_main_menu')
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.clear()
    await callback.message.answer("Вы вернулись в главное меню.", reply_markup=kb.main_menu_kb)