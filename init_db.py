import logging
from src.db.db import init_db

logging.basicConfig(level=logging.INFO)
init_db()
