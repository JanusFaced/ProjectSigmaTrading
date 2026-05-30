from typing import Any
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Enum, Index, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import sys
import enum

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

class PointType(enum.Enum):
    HISTORICAL = "historical"    # исторические данные (тестовая выборка)
    PREDICTION = "prediction"    # предсказанные данные

class Forecast(Base):
    __tablename__ = 'forecasts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    model_type = Column(String(50), default='CatBoost')
    mape_score = Column(Float)
    
    points = relationship("ChartPoint", back_populates="forecast", cascade="all, delete-orphan")


class ChartPoint(Base):
    __tablename__ = 'chart_points'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    forecast_id = Column(Integer, ForeignKey('forecasts.id', ondelete='CASCADE'), nullable=False)
    point_type = Column(Enum(PointType), nullable=False)
    index = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    forecast = relationship("Forecast", back_populates="points")
    
    __table_args__ = (
        Index('idx_forecast_type', 'forecast_id', 'point_type'),
        Index('idx_forecast_index', 'forecast_id', 'index', unique=True),
    )

Base.metadata.create_all(engine)