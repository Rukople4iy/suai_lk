from sqlalchemy.orm import joinedload
from src.db.db import SessionLocal
from src.db.models import Teacher, Discipline, GroupDiscipline, Group, Task, GroupTask, ReportTask, Report
import logging
from datetime import datetime
from sqlalchemy.sql import func

logging.basicConfig(level=logging.INFO)

def get_teacher_by_telegram_id(tg_id):
    db = SessionLocal()
    teacher = db.query(Teacher).filter(Teacher.telegram_id == tg_id).first()
    db.close()
    return teacher

def get_teacher_disciplines(tg_id):
    db = SessionLocal()
    try:
        teacher = db.query(Teacher).filter(Teacher.telegram_id == tg_id).first()
        if not teacher:
            return []

        disciplines = db.query(Discipline).filter(Discipline.teacher_number == teacher.teacher_number).all()
        result = []
        for discipline in disciplines:
            group_disciplines = db.query(GroupDiscipline).filter(GroupDiscipline.discipline == discipline.discipline).all()
            for group_discipline in group_disciplines:
                group = db.query(Group).filter(Group.group_number == group_discipline.group_number).first()
                result.append({
                    "discipline": discipline.discipline,
                    "group_number": group.group_number
                })
        return result
    finally:
        db.close()




def get_groups_for_discipline(discipline_name):
    """
    Возвращает список групп, у которых есть указанная дисциплина
    """
    db = SessionLocal()
    try:
        groups = db.query(Group).join(GroupDiscipline).filter(GroupDiscipline.discipline == discipline_name).all()
        return groups
    finally:
        db.close()


def create_task_for_teacher(discipline, group_numbers, task_name, task_description, task_type, max_score, due_date, file_code):
    db = SessionLocal()

    try:
        # Проверяем существует ли дисциплина
        disc = db.query(Discipline).filter(Discipline.discipline == discipline).first()
        if not disc:
            logging.error(f"Дисциплина {discipline} не найдена.")
            return "Дисциплина не найдена."

        # Создаем задание
        new_task = Task(
            discipline=discipline,
            task_name=task_name,
            task_description=task_description,
            task_type=task_type,
            max_score=max_score,
            due_date=datetime.strptime(due_date, '%d.%m.%Y'),
            file_id=file_code,
            teacher_number=disc.teacher_number  # Предполагается, что дисциплина связана с преподавателем
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        # Создаем задания для каждой группы
        for group_number in group_numbers:
            group = db.query(Group).filter(Group.group_number == group_number).first()
            if not group:
                logging.error(f"Группа {group_number} не найдена.")
                continue

            group_task = GroupTask(
                group_number=group_number,
                task_id=new_task.task_id
            )
            db.add(group_task)

        db.commit()
        logging.info("Задание успешно создано и добавлено в группы.")
        return "Задание успешно создано и добавлено в группы."

    except Exception as e:
        logging.error(f"Произошла ошибка при создании задания: {e}")
        db.rollback()
        return f"Ошибка: {e}"
    finally:
        db.close()

def get_teacher_disciplines_task(teacher_telegram_id: str):
    db = SessionLocal()
    teacher = db.query(Teacher).filter(Teacher.telegram_id == teacher_telegram_id).first()
    if not teacher:
        db.close()
        return []
    disciplines = [d.discipline for d in teacher.disciplines]
    db.close()
    return disciplines

# Получить группы, связанные с дисциплиной
def get_groups_by_discipline(discipline: str):
    db = SessionLocal()
    group_disciplines = db.query(Group).join(Group.group_disciplines).filter_by(discipline=discipline).all()
    db.close()
    return group_disciplines

# Получить задания по дисциплине
def get_tasks_by_discipline(discipline: str):
    db = SessionLocal()
    tasks = db.query(Task).filter(Task.discipline == discipline).order_by(Task.due_date).all()
    db.close()
    return tasks

# Получить список студентов по группе и статус отчетов
def get_students_with_reports_status(group_number: str, task_id: int):
    db = SessionLocal()
    students = db.query(Student).filter(Student.group_number == group_number).all()
    reports = (
        db.query(Report)
        .join(Report.task_reports)
        .filter_by(task_id=task_id)
        .options(joinedload(Report.student))
        .all()
    )

    student_report_status = []
    for student in students:
        report = next((r for r in reports if r.student_number == student.student_number), None)
        if report:
            status_emoji = "✅" if report.report_status == "Проверено" else "📄"
            student_report_status.append((student, status_emoji, report))
        else:
            student_report_status.append((student, "❌", None))
    db.close()
    return student_report_status

# Обновить статус отчета и выставить оценку
def update_report_status(report_id: int, score: float, comment: str = None):
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.report_id == report_id).first()
        if not report:
            return "Отчет не найден."

        report.report_status = "Проверено"
        report.score = score
        report.teacher_comment = comment
        db.commit()
        return "Успешно обновлено."
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()