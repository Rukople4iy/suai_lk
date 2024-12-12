from sqlalchemy.orm import joinedload
from src.db.db import SessionLocal
from src.db.models import Student


def get_student_by_telegram_id(tg_id):
    db = SessionLocal()
    student = db.query(Student).options(joinedload(Student.group)).filter(Student.telegram_id == tg_id).first()
    db.close()
    return student
