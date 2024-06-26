from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Ensure psycopg2-binary is being used
engine = create_engine("postgresql+psycopg2://postgres:sairam2816@localhost/emails")
Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True)
    email_from = Column(String(255), nullable=False)
    email_subject = Column(String(255), nullable=False)
    from_date = Column(String(255), nullable=True)
    to_date = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EmployeeManager(Base):
    __tablename__ = "managers"
    id = Column(Integer, primary_key=True)
    employee_email = Column(String(255), nullable=False)
    manager_email = Column(String(255), nullable=False)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()