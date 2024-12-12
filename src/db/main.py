from .db import init_db, engine
from .models import Base

if __name__ == "__main__":
    init_db(Base)
