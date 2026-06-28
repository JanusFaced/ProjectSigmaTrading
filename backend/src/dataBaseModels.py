from typing import Any
from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    ForeignKey, UniqueConstraint,
    create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
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

class Backtest(Base):
    __tablename__ = 'backtests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    strategy = Column(String(100), nullable=False, unique=True)
    year_profit = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    sharp = Column(Float, nullable=False)
    datetime = Column(DateTime, default=datetime.now)

class Signal(Base):
    __tablename__ = 'signals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    strategy = Column(String(100), nullable=False, unique=True)
    long_signal = Column(String(20), nullable=False)
    short_signal = Column(String(20), nullable=False)
    mode = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    fiat = Column(Float, nullable=False)
    active = Column(Float, nullable=False)
    deposit = Column(Float, nullable=False)
    datetime = Column(DateTime, default=datetime.now)

    trades = relationship("Trade", back_populates="signal_rel", cascade="all, delete-orphan")

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    signal_id = Column(Integer, ForeignKey('signals.id', ondelete='CASCADE'), nullable=False)
    
    long_signal = Column(String(20), nullable=False)
    short_signal = Column(String(20), nullable=False)
    fiat = Column(Float, nullable=False)
    active = Column(Float, nullable=False)
    deposit = Column(Float, nullable=False)
    datetime = Column(DateTime, default=datetime.now)

    signal_rel = relationship("Signal", back_populates="trades")

Base.metadata.create_all(engine)