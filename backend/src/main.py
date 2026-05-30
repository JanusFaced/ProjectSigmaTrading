from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dataBaseModels import Session, Signal, Forecast, ChartPoint, PointType
import os
import sys
from logger_setup import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
	logger.info("Starting FastAPI application")
	yield
	logger.info("Shutting down FastAPI application")

app = FastAPI(
	title="BACKEND API",
	description="Public API для получения торговых сигналов",
	version="1.0.0",
	lifespan=lifespan
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],  # В продакшене на домен
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get('/getTableAnalyst', response_model=list[dict])
async def get_table_analyst():
	dataBaseSession = Session()
	
	try:
		logger.info("Fetching all signals from database")
		signals = dataBaseSession.query(Signal).all()
		
		tableAnalyst = []
		for signal in signals:
			tableAnalyst.append({
				"id": signal.id,
				"asset": signal.asset,
				"ml_model": signal.ml_model,
				"timeframe": signal.timeframe,
				"accuracy": signal.accuracy,
				"signal": signal.signal
			})
		
		logger.info(f"Successfully fetched {len(tableAnalyst)} signals")
		return tableAnalyst
	
	except Exception as e:
		logger.error(f"Error fetching signals: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))
	
	finally:
		dataBaseSession.close()

@app.get('/getForecastsList', response_model=list[dict])
async def get_forecasts_list():
	dataBaseSession = Session()
	
	try:
		forecasts = dataBaseSession.query(Forecast).order_by(Forecast.id.desc()).all()
		
		result = []
		for f in forecasts:
			result.append({
				"id": f.id,
				"symbol": f.symbol,
				"timeframe": f.timeframe,
				"mape_score": f.mape_score
			})
		
		return result
	
	except Exception as e:
		logger.error(f"Error fetching forecasts: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))
	
	finally:
		dataBaseSession.close()

@app.get('/getForecastData/{forecast_id}', response_model=dict)
async def get_forecast_data(forecast_id: int):
	dataBaseSession = Session()
	
	try:		
		forecast = dataBaseSession.query(Forecast).filter(Forecast.id == forecast_id).first()
		if not forecast:
			raise HTTPException(status_code=404, detail="Forecast not found")
		
		points = dataBaseSession.query(ChartPoint).filter(
			ChartPoint.forecast_id == forecast_id
		).order_by(ChartPoint.index).all()

		historical_prices = []
		predicted_prices = []
		
		for p in points:
			point_data = {
				"index": p.index,
				"price": p.price,
				"timestamp": p.timestamp.isoformat()
			}
			
			if p.point_type == PointType.HISTORICAL:
				historical_prices.append(point_data)
			else:
				predicted_prices.append(point_data)

		return {
			"symbol": forecast.symbol,
			"timeframe": forecast.timeframe,
			"mape_score": forecast.mape_score,
			"historical": historical_prices,
			"prediction": predicted_prices
		}
	
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error fetching forecast data: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))
	
	finally:
		dataBaseSession.close()

@app.get('/health')
async def health_check():
	return {"status": "healthy", "framework": "FastAPI"}

@app.get('/')
async def root():
	return {
		"message": "Signals API",
		"version": "1.0.0",
		"endpoints": [
			"/getTableAnalyst",
			"/getForecastsList",
			"/getForecastData/{forecast_id}",
			"/health"
		]
	}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
	logger.error(f"HTTP exception: {exc.detail}")
	return JSONResponse(
		status_code=exc.status_code,
		content={"error": exc.detail}
	)

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
	logger.error(f"Unexpected error: {str(exc)}")
	return JSONResponse(
		status_code=500,
		content={"error": "Internal server error"}
	)