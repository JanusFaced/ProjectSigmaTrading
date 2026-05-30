from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np
from darts import TimeSeries
from dataBaseModels import Session, Forecast, ChartPoint, PointType
from logger_setup import get_logger

logger = get_logger(__name__)

class ForecastService:

	def __init__(self, db_session: Session):
		self.db = db_session

	def save_forecast(
		self,
		symbol: str,
		timeframe: str,
		historical_series: TimeSeries,
		predicted_series: TimeSeries,
		mape: float,
	) -> int:

		old_forecasts = self.db.query(Forecast).filter(
			Forecast.symbol == symbol,
			Forecast.timeframe == timeframe
		).all()
		
		for old in old_forecasts:
			logger.info(f"🗑️ Удаляю старый прогноз #{old.id} для {symbol} {timeframe}")
			self.db.delete(old)
		
		self.db.flush()

		historical_prices = historical_series.values().flatten()
		historical_timestamps = historical_series.time_index
		
		predicted_prices = predicted_series.values().flatten()
		predicted_timestamps = predicted_series.time_index

		forecast = Forecast(
			symbol=symbol,
			timeframe=timeframe,
			mape_score=mape
		)
		
		self.db.add(forecast)
		self.db.flush()
		
		for i, (price, ts) in enumerate(zip(historical_prices, historical_timestamps)):
			point = ChartPoint(
				forecast_id=forecast.id,
				point_type=PointType.HISTORICAL,
				index=i,
				price=float(price),
				timestamp=ts if isinstance(ts, datetime) else datetime.fromisoformat(str(ts))
			)
			self.db.add(point)
		
		start_index = len(historical_prices)
		for i, (price, ts) in enumerate(zip(predicted_prices, predicted_timestamps)):
			point = ChartPoint(
				forecast_id=forecast.id,
				point_type=PointType.PREDICTION,
				index=start_index + i,
				price=float(price),
				timestamp=ts if isinstance(ts, datetime) else datetime.fromisoformat(str(ts))
			)
			self.db.add(point)
		
		self.db.commit()
		
		logger.info(f"✅ Сохранён НОВЫЙ прогноз #{forecast.id}: {len(historical_prices)} исторических + {len(predicted_prices)} предсказанных точек")
		logger.info(f"📊 Для {symbol} {timeframe} теперь актуален только этот прогноз")

		return forecast.id