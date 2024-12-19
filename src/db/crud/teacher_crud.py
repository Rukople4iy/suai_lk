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
    db = SessionLocal()
    try:
        teacher = db.query(Teacher).filter(Teacher.telegram_id == tg_id).first()
        if not teacher:
            return []

        disciplines = db.query(Discipline).filter(Discipline.teacher_number == teacher.teacher_number).all()
        return disciplines
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