from sqlalchemy.orm import joinedload
from src.db.db import SessionLocal
from src.db.models import Users, Teacher, Discipline, GroupDiscipline, Group, Task, GroupTask, ReportTask, Report, Student
import logging

logging.basicConfig(level=logging.INFO)


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




def get_role_by_telegram_id(tg_id):
    db = SessionLocal()
    user = db.query(Users).filter(Users.telegram_id == tg_id).first()
    if user:
        return user.role
    else:
        return None
    db.close()


# на вход report id на выход коммент и оценка, иначе None
def get_report_comment_and_score(report_id):
    db = SessionLocal()
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if report:
        db.close()
        return report.teacher_comment, report.score
    else:
        db.close()
        return None, None