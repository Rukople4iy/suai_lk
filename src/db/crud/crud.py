from sqlalchemy.orm import joinedload
from .db import SessionLocal
from .models import Student



def validate_student_login(login, password):
    db = SessionLocal()
    student = db.query(Student).filter(Student.login == login, Student.password == password).first()
    db.close()
    return student

def update_student_telegram_id(login, tg_id):
    db = SessionLocal()
    student = db.query(Student).filter(Student.login == login).first()
    if student:
        student.telegram_id = tg_id
        db.commit()
    db.close()

def get_students_by_group_number(group_number):
    db = SessionLocal()
    students = db.query(Student).filter(Student.group_number == group_number).all()
    db.close()
    return students
