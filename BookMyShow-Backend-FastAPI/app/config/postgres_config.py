import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
db_url = os.getenv("PGADMIN_DATABASE_URL")

engine = create_engine(db_url)
Session = sessionmaker(autocommit = False, autoflush=False, bind = engine)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()