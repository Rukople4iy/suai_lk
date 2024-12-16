from sqlalchemy.orm import joinedload
from src.db.db import SessionLocal
from src.db.models import Student, Discipline, Teacher, Group, GroupDiscipline


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