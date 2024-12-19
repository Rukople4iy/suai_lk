import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import load_config

logging.basicConfig(level=logging.INFO)

config = load_config()
DATABASE_URL = f"postgresql://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.database}?client_encoding=utf8"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"client_encoding": "utf8"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db(Base):
 
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created.")