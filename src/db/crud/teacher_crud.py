from sqlalchemy.orm import joinedload
from src.db.db import SessionLocal
from src.db.models import Teacher

def get_teacher_by_telegram_id(tg_id):
    db = SessionLocal()
    teacher = db.query(Teacher).filter(Teacher.telegram_id == tg_id).first()
    db.close()
    return teacher
