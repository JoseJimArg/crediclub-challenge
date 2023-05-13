from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://linux:131415@localhost/payments"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
try:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as error:
    print(f'ERROR {error}')

Base = declarative_base()