from sqlalchemy.orm import joinedload
from src.db.db import SessionLocal
from src.db.models import Student, Discipline, Teacher, Group, GroupDiscipline,Report, ReportTask, Task, GroupTask
from datetime import datetime

def get_student_by_telegram_id(tg_id):
    db = SessionLocal()
    student = db.query(Student).options(joinedload(Student.group)).filter(Student.telegram_id == tg_id).first()
    db.close()
    return student


def get_disciplines_and_teachers(tg_id):
    db = SessionLocal()
    student = get_student_by_telegram_id(tg_id)

    if not student:
        return "Студент не найден."

    group_number = student.group_number
    group_disciplines = db.query(GroupDiscipline).filter(GroupDiscipline.group_number == group_number).all()

    if not group_disciplines:
        return "У вас нет назначенных дисциплин."

    result = []
    for group_discipline in group_disciplines:
        discipline = db.query(Discipline).filter(Discipline.discipline == group_discipline.discipline).first()
        teachers = db.query(Teacher).filter(Teacher.teacher_number == discipline.teacher_number).all()
        teacher_names = ", ".join([teacher.fio for teacher in teachers])
        result.append(f"{discipline.discipline} | {teacher_names}")

    db.close()
    return result

def get_group_members(tg_id):
    db = SessionLocal()
    student = get_student_by_telegram_id(tg_id)

    if not student:
        return "Студент не найден."

    group_number = student.group_number
    students = db.query(Student).filter(Student.group_number == group_number).all()

    if not students:
        return "В вашей группе нет студентов."

    result = [student.fio for student in students]
    db.close()
    return result


# список дисциплин студента

def get_student_disciplines(tg_id):
    db = SessionLocal()
    student = get_student_by_telegram_id(tg_id)

    if not student:
        return "Студент не найден."

    group_number = student.group_number
    group_disciplines = db.query(GroupDiscipline).filter(GroupDiscipline.group_number == group_number).all()

    if not group_disciplines:
        return "У вас нет назначенных дисциплин."

    result = []
    for group_discipline in group_disciplines:
        discipline = db.query(Discipline).filter(Discipline.discipline == group_discipline.discipline).first()
        result.append(discipline.discipline)

    db.close()
    return result


# список заданий текущего студента (на входи идет дисциплина и телеграм id студента), возвращаем задание со всеми его атрибутами, сортировка заданий по дате due_date
def get_student_tasks(discipline, tg_id):
    db = SessionLocal()
    student = get_student_by_telegram_id(tg_id)

    if not student:
        return "Студент не найден."

    group_number = student.group_number
    group_disciplines = db.query(GroupDiscipline).filter(GroupDiscipline.group_number == group_number).all()

    if not group_disciplines:
        return "У вас нет назначенных дисциплин."

    result = []
    for group_discipline in group_disciplines:
        if group_discipline.discipline == discipline:
            tasks = db.query(Task).filter(Task.discipline == discipline).order_by(Task.due_date).all()
            for task in tasks:
                result.append(task)

    db.close()
    return result

#получить код файла из таблицы Task, на вход идет task_id
def get_file_code(task_id):
    db = SessionLocal()
    task = db.query(Task).filter(Task.task_id == task_id).first()
    db.close()
    return task.file_id

def add_report(task_id, tg_id, file_code):
    # Создание сессии
    db = SessionLocal()
    try:
        # Получить номер студента по его telegram_id
        student = db.query(Student).filter(Student.telegram_id == tg_id).first()
        if not student:
            return "Студент не найден."

        # Создать новый отчет
        new_report = Report(
            student_number=student.student_number,
            upload_date=datetime.utcnow(),
            report_status='Отправлено',
            file_id=file_code
        )

        # Добавить новый отчет в сессию и коммитить
        db.add(new_report)
        db.commit()  # Коммитим, чтобы получить report_id
        db.refresh(new_report)  # Обновляем объект new_report, чтобы получить присвоенный report_id

        # Создать запись в ReportTask
        new_report_task = ReportTask(
            task_id=task_id,
            report_id=new_report.report_id
        )

        # Добавить запись в ReportTask и коммитить
        db.add(new_report_task)
        db.commit()  # Финальный коммит

        return new_report.report_id
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
