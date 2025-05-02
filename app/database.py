# app/database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

DATABASE_URL = "sqlite:///./assembly_jobs.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class AssemblyJob(Base):
    __tablename__ = "assembly_jobs"

    id = Column(Integer, primary_key=True, index=True)
    left_read = Column(String, nullable=False)
    right_read = Column(String, nullable=False)
    output_dir = Column(String, nullable=False)
    status = Column(String, default="pending")
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    log = Column(Text, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
