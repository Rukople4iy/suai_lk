from sqlalchemy.orm import joinedload
from src.db.db import SessionLocal
from src.db.models import Users, Teacher, Discipline, GroupDiscipline, Group, Task, GroupTask, ReportTask, Report, Student
import logging

logging.basicConfig(level=logging.INFO)
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