from sqlalchemy.orm import joinedload
from src.db.db import SessionLocal
from src.db.models import Users
import logging

logging.basicConfig(level=logging.INFO)

def get_role_by_telegram_id(tg_id):
    db = SessionLocal()
    user = db.query(Users).filter(Users.telegram_id == tg_id).first()
    logging.info(f"user requested: {user.role, user.telegram_id}")
    db.close()
    return user.role
