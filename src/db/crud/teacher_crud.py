from sqlalchemy.orm import joinedload
from src.db.db import SessionLocal
from src.db.models import Teacher, Discipline, GroupDiscipline, Group
import logging

logging.basicConfig(level=logging.INFO)

def get_teacher_by_telegram_id(tg_id):
    db = SessionLocal()
    teacher = db.query(Teacher).filter(Teacher.telegram_id == tg_id).first()
    db.close()
    return teacher

def get_teacher_disciplines(tg_id):
    # Получаем преподавателя по его Telegram ID
    db = SessionLocal()
    teacher = db.query(Teacher).filter(Teacher.telegram_id == tg_id).first()

    if not teacher:
        return "Преподаватель не найден."

    # Получаем дисциплины, которые ведет преподаватель
    disciplines = db.query(Discipline).filter(Discipline.teacher_number == teacher.teacher_number).all()

    if not disciplines:
        return "У вас нет назначенных дисциплин."

    # Формируем список групп и их дисциплин
    result = []
    for discipline in disciplines:
        group_disciplines = db.query(GroupDiscipline).filter(GroupDiscipline.discipline == discipline.discipline).all()
        for group_discipline in group_disciplines:
            group = db.query(Group).filter(Group.group_number == group_discipline.group_number).first()
            result.append(f"{discipline.discipline} | {group.group_number}")
    db.close()
    return result