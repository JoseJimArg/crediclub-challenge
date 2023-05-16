from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os


# load the environment variables
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
try:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as error:
    print(f'ERROR {error}')

Base = declarative_base()