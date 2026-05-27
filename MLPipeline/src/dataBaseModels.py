from typing import Any
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import sys

dataBase_password = os.getenv('DB_PASSWORD')
dataBase_user = os.getenv('DB_USER')
dataBase_name = os.getenv('DB_NAME')
dataBase_host = os.getenv('DB_HOST')
dataBase_port = os.getenv('DB_PORT')

DATABASE_URL = f"postgresql://{dataBase_user}:{dataBase_password}@{dataBase_host}:{dataBase_port}/{dataBase_name}"
engine = create_engine(DATABASE_URL)
Base: Any = declarative_base()
Session = sessionmaker(bind=engine)

class Signal(Base):
    __tablename__ = 'signals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    asset = Column(String(50), nullable=False)
    ml_model = Column(String(100), nullable=False)
    timeframe = Column(String(10), nullable=False)
    signal = Column(String(20), nullable=False)
    accuracy = Column(String(20), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

Base.metadata.create_all(engine)