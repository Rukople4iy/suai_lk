from sqlalchemy.orm import joinedload
from src.db.db import SessionLocal
from src.db.models import Student, Discipline, Teacher, Group, GroupDiscipline,Report, ReportTask, Task, GroupTask
from datetime import datetime


# from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
#
# Base = declarative_base()
#
#
#
# class Group(Base):
#     __tablename__ = "groups"
#     group_number = Column(String, primary_key=True, index=True)
#     institute = Column(String)
#     specialty = Column(String)
#     form_of_study = Column(String)
#     education_level = Column(String)
#     students = relationship("Student", back_populates="group")
#     group_tasks = relationship("GroupTask", back_populates="group")
#     group_disciplines = relationship("GroupDiscipline", back_populates="group")
#
# class Student(Base):
#     __tablename__ = "students"
#     student_number = Column(Integer, primary_key=True, index=True)
#     telegram_id = Column(String, index=True)
#     fio = Column(String)
#     group_number = Column(String, ForeignKey('groups.group_number'))
#     budget_contract = Column(String)
#     group = relationship("Group", back_populates="students")
#     reports = relationship("Report", back_populates="student")
#
# class Teacher(Base):
#     __tablename__ = "teachers"
#     teacher_number = Column(Integer, primary_key=True, index=True)
#     telegram_id = Column(String, index=True)
#     fio = Column(String)
#     department = Column(String)
#     academic_degree = Column(String)
#     email = Column(String)
#     phone = Column(String)
#     disciplines = relationship("Discipline", back_populates="teacher")
#     tasks = relationship("Task", back_populates="teacher")
#
# class Users(Base):
#     __tablename__ = "users"
#     telegram_id = Column(String, primary_key=True, index=True)
#     role = Column(String)
#
# class Task(Base):
#     __tablename__ = "tasks"
#     task_id = Column(Integer, primary_key=True, index=True)
#     discipline = Column(String, ForeignKey('disciplines.discipline'))
#     task_name = Column(String)
#     task_description = Column(String)
#     task_type = Column(String)
#     date_added = Column(DateTime)
#     due_date = Column(DateTime)
#     teacher_number = Column(Integer, ForeignKey('teachers.teacher_number'))
#     max_score = Column(Float)
#     file_id = Column(String)
#     reports = relationship("ReportTask", back_populates="task")
#     group_tasks = relationship("GroupTask", back_populates="task")
#     teacher = relationship("Teacher", back_populates="tasks")
#
# class Report(Base):
#     __tablename__ = "reports"
#     report_id = Column(Integer, primary_key=True, index=True)
#     student_number = Column(Integer, ForeignKey('students.student_number'))
#     upload_date = Column(DateTime)
#     teacher_comment = Column(String)
#     report_status = Column(String)
#     score = Column(Float)
#     file_id = Column(String)
#     task_reports = relationship("ReportTask", back_populates="report")
#     student = relationship("Student", back_populates="reports")
#
# class GroupTask(Base):
#     __tablename__ = "group_tasks"
#     group_number = Column(String, ForeignKey('groups.group_number'), primary_key=True)
#     task_id = Column(Integer, ForeignKey('tasks.task_id'), primary_key=True)
#     group = relationship("Group", back_populates="group_tasks")
#     task = relationship("Task", back_populates="group_tasks")
#
# class Discipline(Base):
#     __tablename__ = "disciplines"
#     discipline = Column(String, primary_key=True, index=True)
#     teacher_number = Column(Integer, ForeignKey('teachers.teacher_number'))
#     teacher = relationship("Teacher", back_populates="disciplines")
#
# class GroupDiscipline(Base):
#     __tablename__ = "group_disciplines"
#     discipline = Column(String, ForeignKey('disciplines.discipline'), primary_key=True)
#     group_number = Column(String, ForeignKey('groups.group_number'), primary_key=True)
#     group = relationship("Group", back_populates="group_disciplines")
#
# class ReportTask(Base):
#     __tablename__ = "report_tasks"
#     task_id = Column(Integer, ForeignKey('tasks.task_id'), primary_key=True)
#     report_id = Column(Integer, ForeignKey('reports.report_id'), primary_key=True)
#     task = relationship("Task", back_populates="reports")
#     report = relationship("Report", back_populates="task_reports")
#

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

def get_report(task_id):
    db = SessionLocal()
    try:
        report_task = db.query(ReportTask).filter(ReportTask.task_id == task_id).first()
        if not report_task:
            return None

        report = db.query(Report).filter(Report.report_id == report_task.report_id).first()
        if not report:
            return None

        task = db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            return None

        return {
            "report_id": report.report_id,
            "score": report.score,
            "report_status": report.report_status,
            "max_score": task.max_score,
            "teacher_comment": report.teacher_comment,
            "upload_date": report.upload_date,
        }
    finally:
        db.close()

def get_file_code_for_report(report_id):
    db = SessionLocal()
    report = db.query(Report).filter(Report.report_id == report_id).first()
    db.close()
    return report.file_id