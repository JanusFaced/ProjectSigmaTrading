from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dataBaseModels import Session, Backtest, Signal, Trade
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
	description="Public API",
	version="1.0.0",
	lifespan=lifespan
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[
#		"https://projectsigmatrading.ru",
#		"http://projectsigmatrading.ru",
#		"https://62.113.37.47",
#		"http://62.113.37.47"
		"*"
	],
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

@app.get('/getTableBacktest', response_model=list[dict])
async def get_table_backtest():
	dataBaseSession = Session()

	try:
		logger.info("Fetching all backtests from database")
		backtests = dataBaseSession.query(Backtest).all()
		
		tableBacktest = []
		for backtest in backtests:
			tableBacktest.append({
				"id": backtest.id,
				"strategy": backtest.strategy,
				"year_profit": backtest.year_profit,
				"max_drawdown": backtest.max_drawdown,
				"sharp": backtest.sharp,
				"datetime": backtest.datetime
			})
		
		logger.info(f"Successfully fetched {len(tableBacktest)} backtests")
		return tableBacktest
	
	except Exception as e:
		logger.error(f"Error fetching backtests: {str(e)}")
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
