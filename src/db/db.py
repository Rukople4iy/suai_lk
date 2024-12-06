import logging
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from config import load_config
from sqlalchemy.orm import joinedload

logging.basicConfig(level=logging.INFO)

config = load_config()
DATABASE_URL = f"postgresql://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.database}?client_encoding=utf8"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"client_encoding": "utf8"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    users = relationship("User", back_populates="group")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)
    group_id = Column(Integer, ForeignKey('groups.id'))
    fio = Column(String)
    institute = Column(String)
    student_id = Column(String)
    specialty = Column(String)
    form_of_study = Column(String)
    education_level = Column(String)
    budget_contract = Column(String)

    group = relationship("Group", back_populates="users")


class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)
    group_id = Column(Integer)


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_user_by_telegram_id(tg_id):
    db = SessionLocal()
    user = db.query(User).options(joinedload(User.group)).filter(User.telegram_id == tg_id).first()
    db.close()
    return user



def validate_user_login(login, password):
    db = SessionLocal()
    user = db.query(User).filter(User.login == login, User.password == password).first()
    db.close()
    return user


def update_telegram_id(login, tg_id):
    db = SessionLocal()
    user = db.query(User).filter(User.login == login).first()
    if user:
        user.telegram_id = tg_id
        db.commit()
    db.close()

def get_users_by_group_id(group_id):
    db = SessionLocal()
    users = db.query(User).filter(User.group_id == group_id).all()
    db.close()
    return users





if __name__ == "__main__":
    init_db()
