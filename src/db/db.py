from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import load_config

config = load_config()
DATABASE_URL = f"postgresql://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.database}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class User(Base):
    __tablename__ = "users"
    telegram_id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)
    group_id = Column(Integer)

def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    groups = [Group(name="Группа 1"), Group(name="Группа 2")]
    db.add_all(groups)
    admin = User(telegram_id=123456789, login="admin", password="adminpass", role="admin")
    db.add(admin)
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
