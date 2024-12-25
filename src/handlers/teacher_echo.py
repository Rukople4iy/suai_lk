from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import CommandStart
import src.db.crud.teacher_crud as crud
import src.db.crud.common_crud as common_crud
import src.keyboards.teacher_kb as kb
from datetime import datetime
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

router_main: Router = Router()


# Хэндлер для callback_data "us_show_groups"
@router_main.callback_query(F.data == 'show_teacher_disciplines')
async def show_group_members(callback: CallbackQuery):
    await callback.answer('')
    disciplines = crud.get_teacher_disciplines_groups(str(callback.from_user.id))

    if not disciplines:
        await callback.message.answer("У вас нет назначенных дисциплин.")
        return

    result_list = "\n".join([f"{d['discipline']} | {d['group_number']}" for d in disciplines])
    message_text = f"Дисциплина | Группа\n{result_list}"

    await callback.message.answer(message_text, reply_markup=kb.main_menu_kb)


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
    await callback.message.answer(f"Введите номер дисциплины\n{discipline_list}", reply_markup=kb.back_to_main_menu_kb)
    await state.set_state(TaskForm.discipline)


@router_main.message(TaskForm.discipline)
async def process_discipline(message: Message, state: FSMContext):
    discipline_choice = int(message.text) - 1
    teacher_telegram_id = message.from_user.id
    disciplines = crud.get_teacher_disciplines(str(teacher_telegram_id))
    chosen_discipline = disciplines[discipline_choice]['discipline']

    await state.update_data(discipline=chosen_discipline)

    groups = crud.get_groups_for_discipline(chosen_discipline)
    if not groups:
        await message.answer("Нет групп для выбранной дисциплины.")
        return

    group_list = "\n".join([f"{g.group_number}" for idx, g in enumerate(groups)])
    await message.answer(f"Введите номера групп через пробел\n{group_list}", reply_markup=kb.back_to_main_menu_kb)
    await state.set_state(TaskForm.groups)


@router_main.message(TaskForm.groups)
async def process_groups(message: Message, state: FSMContext):
    group_numbers = message.text.split()
    await state.update_data(groups=group_numbers)
    await message.answer("Введите наименование задания", reply_markup=kb.back_to_main_menu_kb)
    await state.set_state(TaskForm.task_name)


@router_main.message(TaskForm.task_name)
async def process_task_name(message: Message, state: FSMContext):
    await state.update_data(task_name=message.text)
    await message.answer("Введите описание задания", reply_markup=kb.back_to_main_menu_kb)
    await state.set_state(TaskForm.task_description)


@router_main.message(TaskForm.task_description)
async def process_task_description(message: Message, state: FSMContext):
    await state.update_data(task_description=message.text)
    await message.answer(
        "Введите номер типа задания\n1. Лабораторная работа\n2. Индивидуальное задание\n3. Расчетно-графическая работа\n4. Курсовой проект (работа)\n5. Практические задания\n6. Отчет о научных исследованиях\n7. Эссе\n8. Реферат", reply_markup=kb.back_to_main_menu_kb)
    await state.set_state(TaskForm.task_type)


@router_main.message(TaskForm.task_type)
async def process_task_type(message: Message, state: FSMContext):
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
    await message.answer("Введите количество баллов задания", reply_markup=kb.back_to_main_menu_kb)
    await state.set_state(TaskForm.max_score)


@router_main.message(TaskForm.max_score)
async def process_max_score(message: Message, state: FSMContext):
    await state.update_data(max_score=message.text)
    await message.answer("Введите предельную дату выполнения в формате ДД.ММ.ГГГГ", reply_markup=kb.back_to_main_menu_kb)
    await state.set_state(TaskForm.due_date)


@router_main.message(TaskForm.due_date)
async def process_due_date(message: Message, state: FSMContext):
    due_date_str = message.text
    try:
        # Проверка формата даты
        due_date = datetime.strptime(due_date_str, "%d.%m.%Y").date()

        # Проверка, что дата в будущем
        if due_date <= datetime.now().date():
            raise ValueError("Предельная дата выполнения должна быть в будущем.")

        await state.update_data(due_date=due_date_str)
        await message.answer("Загрузите дополнительный материал (максимум 1 файл)", reply_markup=kb.back_to_main_menu_kb)
        await state.set_state(TaskForm.file_code)

    except ValueError as e:
        await message.answer(f"Некорректная дата: {str(e)}. Пожалуйста, введите корректную дату в формате ДД.ММ.ГГГГ.")
        await state.set_state(TaskForm.due_date)



# Обработка документа
async def handle_task_form_file(message: Message, state: FSMContext):
    logging.info("Файл получен для TaskForm.")
    file_code = message.document.file_id
    logging.info("получен id файла.")
    await state.update_data(file_code=file_code)
    logging.info("Файл id сохранен в состояние.")
    await message.answer("Готово. Задание сформировано и будет отправлено в базу данных.", reply_markup=kb.main_menu_kb)

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
# class CheckTaskForm(StatesGroup):
#     discipline = State()
#     group = State()
#     task = State()
#     student = State()
#     score = State()
#     comment = State()
#
#
# @router_main.callback_query(F.data == 'check_task_teacher')
# async def start_checking(callback: CallbackQuery, state: FSMContext):
#     await callback.answer()
#     teacher_id = callback.from_user.id
#     disciplines = crud.get_teacher_disciplines_task(str(teacher_id))
#
#     if not disciplines:
#         await callback.message.answer("У вас нет назначенных дисциплин.")
#         return
#
#     await state.update_data(disciplines=disciplines)  # Сохраняем данные дисциплин в состояние
#
#     discipline_list = "\n".join(
#         [f"{idx + 1}. {d['discipline']}" for idx, d in enumerate(disciplines)])
#     await callback.message.answer(f"Введите номер дисциплины:\n{discipline_list}")
#     await state.set_state(CheckTaskForm.discipline)
#
#
# @router_main.message(CheckTaskForm.discipline)
# async def choose_group(message: Message, state: FSMContext):
#     discipline_index = int(message.text.strip()) - 1
#     data = await state.get_data()
#     disciplines = data.get("disciplines", [])
#
#     if discipline_index < 0 or discipline_index >= len(disciplines):
#         await message.answer("Неверный номер дисциплины. Попробуйте снова.")
#         return
#
#     selected_discipline = disciplines[discipline_index]["discipline"]
#     groups = crud.get_groups_by_discipline(selected_discipline)
#
#     if not groups:
#         await message.answer("Нет доступных групп для этой дисциплины.")
#         await state.clear()
#         return
#
#     await state.update_data(selected_discipline=selected_discipline)
#
#     group_list = "\n".join(
#         [f"{idx + 1}. {g['group_number']} ({g['unreviewed_count']} не проверено)" for idx, g in enumerate(groups)])
#     await message.answer(f"Введите номер группы:\n{group_list}")
#     await state.set_state(CheckTaskForm.group)
#
#
# @router_main.message(CheckTaskForm.group)
# async def choose_task(message: Message, state: FSMContext):
#     group_index = int(message.text.strip()) - 1
#     data = await state.get_data()
#     selected_discipline = data.get("selected_discipline")
#     groups = crud.get_groups_by_discipline(selected_discipline)
#
#     if group_index < 0 or group_index >= len(groups):
#         await message.answer("Неверный номер группы. Попробуйте снова.")
#         return
#
#     selected_group = groups[group_index]["group_number"]
#     tasks = crud.get_tasks_by_group(selected_group)
#
#     if not tasks:
#         await message.answer("Нет доступных заданий для этой группы.")
#         await state.clear()
#         return
#
#     await state.update_data(selected_group=selected_group)
#
#     task_list = "\n".join(
#         [f"{idx + 1}. {t['task_name']} ({t['unreviewed_count']} не проверено)" for idx, t in enumerate(tasks)])
#     await message.answer(f"Введите номер задания:\n{task_list}")
#     await state.set_state(CheckTaskForm.task)
#
#
# @router_main.message(CheckTaskForm.task)
# async def choose_student(message: Message, state: FSMContext):
#     task_index = int(message.text.strip()) - 1
#     data = await state.get_data()
#     selected_group = data.get("selected_group")
#     tasks = crud.get_tasks_by_group(selected_group)
#
#     if task_index < 0 or task_index >= len(tasks):
#         await message.answer("Неверный номер задания. Попробуйте снова.")
#         return
#
#     selected_task = tasks[task_index]["task_name"]
#     students = crud.get_students_by_task(selected_task)
#
#     if not students:
#         await message.answer("Нет студентов с загруженными отчётами для этого задания.")
#         await state.clear()
#         return
#
#     await state.update_data(selected_task=selected_task)
#
#     student_list = "\n".join([f"{idx + 1}. {s['name']}" for idx, s in enumerate(students)])
#     await message.answer(f"Введите номер студента:\n{student_list}")
#     await state.set_state(CheckTaskForm.student)
#
#
# @router_main.message(CheckTaskForm.student)
# async def review_report(message: Message, state: FSMContext):
#     student_index = int(message.text.strip()) - 1
#     data = await state.get_data()
#     selected_task = data.get("selected_task")
#     students = crud.get_students_by_task(selected_task)
#
#     if student_index < 0 or student_index >= len(students):
#         await message.answer("Неверный номер студента. Попробуйте снова.")
#         return
#
#     selected_student = students[student_index]["name"]
#     report = crud.get_report_by_student(selected_student)
#
#     if not report:
#         await message.answer("Отчёт не найден для этого студента.")
#         await state.clear()
#         return
#
#     await state.update_data(selected_student=selected_student)
#
#     await message.answer(
#         f"Задание: {report['task_name']}\nГруппа: {report['group_number']}\nСтудент: {report['student_name']}\nДата сдачи: {report['submission_date']}\n\nФайл отчёта: {report['file_url']}")
#     await message.answer(f"Введите баллы (макс. {report['max_score']}):")
#     await state.set_state(CheckTaskForm.score)
#
#
# @router_main.message(CheckTaskForm.score)
# async def add_comment(message: Message, state: FSMContext):
#     score = int(message.text.strip())
#     await state.update_data(score=score)
#     await message.answer("Напишите комментарий:")
#     await state.set_state(CheckTaskForm.comment)
#
#
# @router_main.message(CheckTaskForm.comment)
# async def finish_review(message: Message, state: FSMContext):
#     comment = message.text.strip()
#     data = await state.get_data()
#     score = data.get("score")
#     selected_student = data.get("selected_student")
#
#     crud.save_review(student=selected_student, score=score, comment=comment)
#
#     await message.answer("Проверка завершена. Данные сохранены.")
#     await state.clear()


class CheckReports(StatesGroup):
    discipline_st = State()
    group = State()
    task = State()
    student = State()
    mid_choose = State()
    report = State()
    comment = State()
    estimation = State()
    approve = State()

# Начало проверки заданий
@router_main.callback_query(F.data == 'check_task_teacher')
async def check_task_teacher(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    disciplines = crud.get_teacher_disciplines_task(str(callback.from_user.id))
    if not disciplines:
        await callback.message.answer("У вас нет назначенных дисциплин.")
        return

    result_list = "\n".join(f"{i + 1}. {d}" for i, d in enumerate(disciplines))
    await callback.message.answer(f"Выберите дисциплину, введя её номер:\n{result_list}", reply_markup=kb.back_to_main_menu_kb)

    logging.info("смениил состояние")
    await state.set_state(CheckReports.discipline_st)
    await state.update_data(disciplines=disciplines)
    logging.info(f"Текущее состояние: {await state.get_state()}")


# Выбор дисциплины
@router_main.message(CheckReports.discipline_st)
async def select_discipline_report(message: Message, state: FSMContext):
    logging.info(f"Получено сообщение: {message.text}")

    logging.info(f"Текущее состояние при входе в хэндлер: {await state.get_state()}")

    state_data = await state.get_data()
    disciplines = state_data.get('disciplines')
    selected_number = int(message.text.strip()) - 1
    logging.info("проверка ввода")
    if isinstance(selected_number, int) and 0 <= selected_number < len(disciplines):
        logging.info("корректный ввод")
        selected_discipline = disciplines[selected_number]
        groups = crud.get_groups_by_discipline(selected_discipline)
        if not groups:
            await message.answer("Нет групп для этой дисциплины.")
            await state.clear()
            return

        result_list = "\n".join(f"{i + 1}. {g.group_number}" for i, g in enumerate(groups))
        await message.answer(f"Выберите группу, введя её номер:\n{result_list}", reply_markup=kb.back_to_main_menu_kb)
        await state.update_data(selected_discipline=selected_discipline, groups=groups)
        await state.set_state(CheckReports.group)
    else:
        await message.answer("Некорректный номер. Пожалуйста, выберите правильный номер дисциплины.")

# Выбор группы
@router_main.message(CheckReports.group)
async def select_group_report(message: Message, state: FSMContext):
    state_data = await state.get_data()
    groups = state_data.get('groups')
    selected_number = int(message.text.strip()) - 1
    await state.update_data(message_tasks=message)
    if isinstance(selected_number, int) and 0 <= selected_number < len(groups):
        selected_group = groups[selected_number]
        tasks = crud.get_tasks_by_discipline(state_data.get('selected_discipline'))
        if not tasks:
            await message.answer("Нет заданий для этой дисциплины.")
            await state.clear()
            return

        result_list = "\n".join(f"{i + 1}. {t.task_name}" for i, t in enumerate(tasks))
        await message.answer(f"Выберите задание, введя его номер:\n{result_list}", reply_markup=kb.back_to_main_menu_kb)
        await state.update_data(selected_group=selected_group, tasks=tasks)
        await state.set_state(CheckReports.task)
    else:
        await message.answer("Некорректный номер. Пожалуйста, выберите правильный номер группы.")


#callback back_to_main_menu_teacher
@router_main.callback_query(F.data == 'back_to_main_menu_teacher')
async def back_to_main_menu_teacher(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.answer("Выберите категорию", reply_markup=kb.main_menu_kb)
    await state.clear()

@router_main.callback_query(F.data == 'back_to_tasks_teacher')
async def back_to_tasks_teacher(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    state_data = await state.get_data()
    message = state_data.get('message_tasks')
    await select_group_report(message, state)


# Выбор задания
@router_main.message(CheckReports.task)
async def select_task_report(message: Message, state: FSMContext):
    state_data = await state.get_data()
    tasks = state_data.get('tasks')
    selected_number = int(message.text.strip()) - 1
    await state.update_data(message_student=message)
    if isinstance(selected_number, int) and 0 <= selected_number < len(tasks):
        selected_task = tasks[selected_number]
        students = await crud.get_students_with_reports_status(state_data.get('selected_group').group_number, selected_task.task_id)
        if not students:
            await message.answer("Нет студентов с отчетами для этого задания.")
            await state.clear()
            return

        result_list = "\n".join(f"{i + 1}. {s[0].fio} {s[1]}" for i, s in enumerate(students))
        await message.answer(f"Выберите студента, введя его номер:\n{result_list}", reply_markup=kb.choose_student_kb)
        await state.update_data(selected_task=selected_task, students=students)
        await state.set_state(CheckReports.student)
    else:
        await message.answer("Некорректный номер. Пожалуйста, выберите правильный номер задания.")


# Выбор студента
@router_main.message(CheckReports.student)
async def select_student_report(message: Message, state: FSMContext):
    state_data = await state.get_data()
    students = state_data.get('students')
    selected_number = int(message.text.strip()) - 1

    if isinstance(selected_number, int) and 0 <= selected_number < len(students):
        selected_student, emoji, report = students[selected_number]
        if report:
            task = state_data.get('selected_task')
            await state.update_data(message_estimate=message)
            comment, score = common_crud.get_report_comment_and_score(report.report_id)
            max_score = crud.get_task_max_score_by_report(report.report_id)
            if score != None:

                await message.answer(
                    f"Задание: {task.task_name}\nГруппа: {state_data.get('selected_group').group_number}\n"
                    f"ФИО студента: {selected_student.fio}\nДата отправки: {report.upload_date}\n"
                    "\nОценено вами:\n"
                    f"Комментарий: {comment}\nОценка: {score}/{max_score}",
                    reply_markup=kb.generate_teacher_report_kb(report.report_id, ischecked=True)
                )
            else:
                await message.answer(
                    f"Задание: {task.task_name}\nГруппа: {state_data.get('selected_group').group_number}\n"
                    f"ФИО студента: {selected_student.fio}\nДата отправки: {report.upload_date}\n",
                    reply_markup=kb.generate_teacher_report_kb(report.report_id, ischecked=False)
                )

            await state.set_state()
        else:
            await message.answer("У этого студента нет отчета.")
    else:
        await message.answer("Некорректный номер. Пожалуйста, выберите правильный номер студента.")



# @router_main.message(CheckReports.mid_choose)
# async def
#     state_data = await state.get_data()
#     tasks = state_data.get('tasks')


@router_main.callback_query(F.data == 'back_to_students')
async def approve_report(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    state_data = await state.get_data()
    message = state_data.get('message_student')
    await select_task_report(message, state)



@router_main.callback_query(F.data.startswith('view_report:'))
async def view_report(callback: CallbackQuery):
    selected_report_id = callback.data.split(':')[1]
    await callback.answer('')
    file = crud.get_file_code(selected_report_id)
    await callback.message.answer_document(file)

@router_main.callback_query(F.data.startswith('estimate_report:'))
async def estimate_report(callback: CallbackQuery, state: FSMContext):
    selected_report_id = callback.data.split(':')[1]
    await callback.answer('')
    await state.set_state(CheckReports.estimation)
    await state.update_data(selected_report_id=selected_report_id)

    max_score = crud.get_task_max_score_by_report(selected_report_id)
    await state.update_data(max_score=max_score)
    await callback.message.answer(f"Введите баллы (макс. {max_score}):")

@router_main.message(CheckReports.estimation)
async def set_estimation_report(message: Message, state: FSMContext):
    user_input = message.text
    max_score = (await state.get_data()).get('max_score')

    try:
        score = float(user_input)
        if 0 <= score <= max_score:
            await state.update_data(score=score)
            await message.answer("Баллы успешно сохранены! Напишите комментарий к отчету для студента:")
            await state.update_data(score=score)
            await state.set_state(CheckReports.comment)
            # Дальнейшие действия по сохранению данных или переходу к следующему этапу
        else:
            raise ValueError("Invalid score range")
    except ValueError:
        await message.answer(f"Некорректное значение. Пожалуйста, введите число от 0 до {max_score}.")


@router_main.message(CheckReports.comment)
async def set_comment_report(message: Message, state: FSMContext):
    user_input = message.text
    await state.update_data(comment=user_input)
    await state.set_state(CheckReports.approve)
    max_score = (await state.get_data()).get('max_score')
    score = (await state.get_data()).get('score')
    await message.answer(f"Оценка: {score}/{max_score}\nКомментарий:{user_input}\n\nПодтвердите отправку отчета студенту:", reply_markup=kb.approve_report_kb)

# оповещение что данные сохранены
@router_main.callback_query(F.data == 'approve_report')
@router_main.message(CheckReports.approve)
async def approve_report(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    data = await state.get_data()
    selected_report_id = data.get('selected_report_id')
    score = data.get('score')
    comment = data.get('comment')
    result = crud.save_report_details(selected_report_id, score, comment)
    await callback.message.answer("Оценка успешно сохранена!" if result == "Успешно обновлено." else result)
    state_data = await state.get_data()
    message_estimate = state_data.get('message_estimate')
    await select_task_report(message_estimate, state)



@router_main.callback_query(F.data == 'reject_report')
@router_main.message(CheckReports.approve)
async def reject_report(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    state_data = await state.get_data()
    message_estimate = state_data.get('message_estimate')
    await callback.message.answer("Оценка отменена!")
    await select_student_report(message_estimate, state)