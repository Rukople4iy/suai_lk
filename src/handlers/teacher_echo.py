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


# Хэндлер для callback_data "us_show_groups"
@router_main.callback_query(F.data == 'show_teacher_disciplines')
async def show_group_members(callback: CallbackQuery):
    await callback.answer('')
    disciplines = crud.get_teacher_disciplines(str(callback.from_user.id))

    if not disciplines:
        await callback.message.answer("У вас нет назначенных дисциплин.")
        return

    result_list = "\n".join([f"{d['discipline']} | {d['group_number']}" for d in disciplines])
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
    await callback.answer('')
    teacher_telegram_id = callback.from_user.id
    disciplines = crud.get_teacher_disciplines(str(teacher_telegram_id))

    if not disciplines:
        await callback.message.answer("У вас нет назначенных дисциплин.")
        return

    discipline_list = "\n".join([f"{idx + 1}. {d['discipline']}" for idx, d in enumerate(disciplines)])
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
        chosen_discipline = disciplines[discipline_choice]['discipline']

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
        #Сохраняем название типа задания в базу данных из выбранного номера
        task_types = {
            "1": "Лабораторная работа",
            "2": "Индивидуальное задание",
            "3": "Расчетно-графическая работа",
            "4": "Курсовой проект (работа)",
            "5": "Практические задания",
            "6": "Отчет о научных исследованиях",
            "7": "Эссе",
            "8": "Реферат"
        }
        await state.update_data(task_type=task_types[message.text])



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

# Обработка документа
async def handle_task_form_file(message: Message, state: FSMContext):
    logging.info("Файл получен для TaskForm.")
    file_code = message.document.file_id
    logging.info("получен id файла.")
    await state.update_data(file_code=file_code)
    logging.info("Файл id сохранен в состояние.")
    await message.answer("Готово. Задание сформировано и будет отправлено в базу данных.")

    # Retrieve data from state and send to database
    data = await state.get_data()
    crud.create_task_for_teacher(
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
    await state.clear()






#
# class CheckReports(StatesGroup):
#     discipline_st = State()
#     group = State()
#     task = State()
#     student = State()
#     report = State()
#
# # Начало проверки заданий
# @router_main.callback_query(F.data == 'check_task_teacher')
# async def check_task_teacher(callback: CallbackQuery, state: FSMContext):
#     await callback.answer('')
#     disciplines = crud.get_teacher_disciplines_task(str(callback.from_user.id))
#     if not disciplines:
#         await callback.message.answer("У вас нет назначенных дисциплин.")
#         return
#
#     result_list = "\n".join(f"{i + 1}. {d}" for i, d in enumerate(disciplines))
#     await callback.message.answer(f"Выберите дисциплину, введя её номер:\n{result_list}")
#
#     logging.info("смениил состояние")
#     await state.set_state(CheckReports.discipline_st)
#     await state.update_data(disciplines=disciplines)
#     logging.info(f"Текущее состояние: {await state.get_state()}")
#
#
# # Выбор дисциплины
# @router_main.message(CheckReports.discipline_st)
# async def select_discipline_report(message: Message, state: FSMContext):
#     logging.info(f"Получено сообщение: {message.text}")
#
#     logging.info(f"Текущее состояние при входе в хэндлер: {await state.get_state()}")
#
#     state_data = await state.get_data()
#     disciplines = state_data.get('disciplines')
#     selected_number = int(message.text.strip()) - 1
#     logging.info("проверка ввода")
#     if 0 <= selected_number < len(disciplines):
#         logging.info("корректный ввод")
#         selected_discipline = disciplines[selected_number]
#         groups = crud.get_groups_by_discipline(selected_discipline)
#         if not groups:
#             await message.answer("Нет групп для этой дисциплины.")
#             await state.clear()
#             return
#
#         result_list = "\n".join(f"{i + 1}. {g.group_number}" for i, g in enumerate(groups))
#         await message.answer(f"Выберите группу, введя её номер:\n{result_list}")
#         await state.update_data(selected_discipline=selected_discipline, groups=groups)
#         await state.set_state(CheckReports.group)
#     else:
#         await message.answer("Некорректный номер. Пожалуйста, выберите правильный номер дисциплины.")
#
# # Выбор группы
# @router_main.message(CheckReports.group)
# async def select_group_report(message: Message, state: FSMContext):
#     state_data = await state.get_data()
#     groups = state_data.get('groups')
#     selected_number = int(message.text.strip()) - 1
#
#     if 0 <= selected_number < len(groups):
#         selected_group = groups[selected_number]
#         tasks = crud.get_tasks_by_discipline(state_data.get('selected_discipline'))
#         if not tasks:
#             await message.answer("Нет заданий для этой дисциплины.")
#             await state.clear()
#             return
#
#         result_list = "\n".join(f"{i + 1}. {t.task_name}" for i, t in enumerate(tasks))
#         await message.answer(f"Выберите задание, введя его номер:\n{result_list}")
#         await state.update_data(selected_group=selected_group, tasks=tasks)
#         await state.set_state(CheckReport.task)
#     else:
#         await message.answer("Некорректный номер. Пожалуйста, выберите правильный номер группы.")
#
# # Выбор задания
# @router_main.message(CheckReports.task)
# async def select_task_report(message: Message, state: FSMContext):
#     state_data = await state.get_data()
#     tasks = state_data.get('tasks')
#     selected_number = int(message.text.strip()) - 1
#
#     if 0 <= selected_number < len(tasks):
#         selected_task = tasks[selected_number]
#         students = crud.get_students_with_reports_status(state_data.get('selected_group').group_number, selected_task.task_id)
#         if not students:
#             await message.answer("Нет студентов с отчетами для этого задания.")
#             await state.clear()
#             return
#
#         result_list = "\n".join(f"{i + 1}. {s[0].fio} {s[1]}" for i, s in enumerate(students))
#         await message.answer(f"Выберите студента, введя его номер:\n{result_list}")
#         await state.update_data(selected_task=selected_task, students=students)
#         await state.set_state(CheckReports.student)
#     else:
#         await message.answer("Некорректный номер. Пожалуйста, выберите правильный номер задания.")
#
# # Выбор студента
# @router_main.message(CheckReports.student)
# async def select_student_report(message: Message, state: FSMContext):
#     state_data = await state.get_data()
#     students = state_data.get('students')
#     selected_number = int(message.text.strip()) - 1
#
#     if 0 <= selected_number < len(students):
#         selected_student, emoji, report = students[selected_number]
#         if report:
#             task = state_data.get('selected_task')
#             await message.answer(
#                 f"Задание: {task.task_name}\nГруппа: {state_data.get('selected_group').group_number}\n"
#                 f"ФИО студента: {selected_student.fio}\nДата отправки: {report.upload_date}\n",
#                 reply_markup=kb.generate_teacher_report_kb(report.report_id)
#             )
#             await state.clear()
#         else:
#             await message.answer("У этого студента нет отчета.")
#     else:
#         await message.answer("Некорректный номер. Пожалуйста, выберите правильный номер студента.")