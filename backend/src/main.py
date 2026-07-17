from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dataBaseModels import Backtest, Signal, Trade
from dataBaseModels import get_session, close_session
import os
from logger_setup import get_logger

logger = get_logger(__name__)

MODE_WORK = os.getenv('MODE_WORK')
ADMIN_KEY = os.getenv('ADMIN_KEY')

if MODE_WORK == 'localhost':
	allow_origins = ['*']
elif MODE_WORK == 'server':
	allow_origins = [
		"https://projectsigmatrading.ru",
		"http://projectsigmatrading.ru",
		"https://62.113.37.47",
		"http://62.113.37.47"
	]

def verify_admin_key(x_api_key: str = Header(...)):
	if x_api_key != ADMIN_KEY:
		logger.warning(f"Invalid admin API key attempt")
		raise HTTPException(status_code=403, detail="Invalid admin API key")
	return True

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
	allow_origins=allow_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get('/getTableBacktest', response_model=list[dict])
async def get_table_backtest():
	dataBaseSession = get_session()

	try:
		logger.info("Fetching all backtests from database")
		backtests = dataBaseSession.query(Backtest).order_by(Backtest.year_profit.desc()).all()
		
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
		close_session()

@app.get('/getTableAnalyst', response_model=list[dict])
async def get_table_analyst():
	dataBaseSession = get_session()

	try:
		logger.info("Fetching all signals from database")
		signals = dataBaseSession.query(Signal).order_by(Signal.deposit.desc()).all()
		
		tableAnalyst = []
		for signal in signals:
			tableAnalyst.append({
				"id": signal.id,
				"strategy": signal.strategy,
				"long_signal": "long_open" if signal.long_signal == "-1" else "long_close",
				"short_signal": "short_open" if signal.short_signal == "1" else "short_close",
				"mode": signal.mode,
				"status": signal.status,
				"fiat": str(round(signal.fiat, 2)),
				"active": str(round(signal.active, 2)),
				"deposit": str(round(signal.deposit, 2)),
				"datetime": str(signal.datetime.strftime("%Y-%m-%d %H:%M"))
			})
		
		logger.info(f"Successfully fetched {len(tableAnalyst)} signals")
		return tableAnalyst
	
	except Exception as e:
		logger.error(f"Error fetching signals: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))
	
	finally:
		close_session()

@app.get('/getTradesBySignal/{signal_id}', response_model=dict)
async def get_trades_by_signal(
		signal_id: int,
		page: int = Query(1, ge=1),
		limit: int = Query(50, ge=1, le=500),
		chart_limit: int = Query(50)
	):
	dataBaseSession = get_session()
	
	try:
		logger.info(f"Fetching trades for signal ID: {signal_id}")
		
		signal = dataBaseSession.query(Signal).filter(Signal.id == signal_id).first()
		if not signal:
			logger.warning(f"Signal with ID {signal_id} not found")
			raise HTTPException(status_code=404, detail="Signal not found")
		
		total_trades_count = dataBaseSession.query(Trade).filter(Trade.signal_id == signal_id).count()
		
		chart_query = dataBaseSession.query(Trade).filter(
			Trade.signal_id == signal_id
		).order_by(Trade.datetime.desc())
		
		if chart_limit != -1:
			chart_query = chart_query.limit(chart_limit)
		
		chart_trades = chart_query.all()
		chart_trades = chart_trades[::-1]
		
		offset = (page - 1) * limit
		table_trades = dataBaseSession.query(Trade).filter(
			Trade.signal_id == signal_id
		).order_by(Trade.datetime.desc()).offset(offset).limit(limit).all()
		
		chartData = []
		for trade in chart_trades:
			chartData.append({
				"id": trade.id,
				"deposit": str(round(trade.deposit, 2)),
				"datetime": str(trade.datetime.strftime("%Y-%m-%d %H:%M")) if trade.datetime else "N/A"
			})
		
		tableData = []
		for trade in table_trades:
			tableData.append({
				"id": trade.id,
				"deposit": str(round(trade.deposit, 2)),
				"datetime": str(trade.datetime.strftime("%Y-%m-%d %H:%M")) if trade.datetime else "N/A"
			})

		total_pages = (total_trades_count + limit - 1) // limit if total_trades_count > 0 else 1
		
		logger.info(f"Successfully fetched trades for signal {signal_id}")
		
		return {
			"strategy": signal.strategy,
			"chart_data": chartData,
			"table_data": tableData,
			"pagination": {
				"current_page": page,
				"limit": limit,
				"total": total_trades_count,
				"total_pages": total_pages
			},
			"statistics": {
				"total_trades": total_trades_count
			}
		}
	
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error fetching trades for signal {signal_id}: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))
	
	finally:
		close_session()

@app.delete('/admin/delete-signal/{signal_id}')
async def delete_signal(
		signal_id: int,
		admin_key: bool = Depends(verify_admin_key)
	):
	dataBaseSession = get_session()
	
	try:
		logger.info(f"Admin: Attempting to delete signal ID: {signal_id}")
		
		signal = dataBaseSession.query(Signal).filter(Signal.id == signal_id).first()
		if not signal:
			logger.warning(f"Signal with ID {signal_id} not found")
			raise HTTPException(status_code=404, detail="Signal not found")
		
		signal_name = signal.strategy
		trades_count = dataBaseSession.query(Trade).filter(Trade.signal_id == signal_id).count()
		
		deleted_trades = dataBaseSession.query(Trade).filter(Trade.signal_id == signal_id).delete()
		logger.info(f"Deleted {deleted_trades} trades for signal {signal_id}")
		
		dataBaseSession.delete(signal)
		dataBaseSession.commit()
		
		logger.info(f"Successfully deleted signal '{signal_name}' (ID: {signal_id}) with {deleted_trades} trades")
		
		return {
			"success": True,
			"message": f"Сигнал '{signal_name}' успешно удален",
			"deleted_signal_id": signal_id,
			"deleted_trades_count": deleted_trades,
			"signal_name": signal_name
		}
		
	except HTTPException:
		raise
	except Exception as e:
		dataBaseSession.rollback()
		logger.error(f"Error deleting signal {signal_id}: {str(e)}")
		raise HTTPException(status_code=500, detail=f"Error deleting signal: {str(e)}")
	
	finally:
		close_session()

@app.get('/admin/statistics')
async def get_admin_statistics(
		admin_key: bool = Depends(verify_admin_key)
	):
	dataBaseSession = get_session()
	
	try:
		signals_count = dataBaseSession.query(Signal).count()
		backtests_count = dataBaseSession.query(Backtest).count()
		trades_count = dataBaseSession.query(Trade).count()
		
		signals = dataBaseSession.query(Signal).all()
		signals_list = []
		for signal in signals:
			trades = dataBaseSession.query(Trade).filter(Trade.signal_id == signal.id).count()
			signals_list.append({
				"id": signal.id,
				"strategy": signal.strategy,
				"deposit": signal.deposit,
				"status": signal.status,
				"trades_count": trades,
				"datetime": signal.datetime.strftime("%Y-%m-%d %H:%M") if signal.datetime else "N/A"
			})
		
		return {
			"total_signals": signals_count,
			"total_backtests": backtests_count,
			"total_trades": trades_count,
			"signals": signals_list
		}
		
	except Exception as e:
		logger.error(f"Error getting admin statistics: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))
	
	finally:
		close_session()

@app.get('/health')
async def health_check():
	return {"status": "healthy", "framework": "FastAPI"}

@app.get('/')
async def root():
	return {
		"message": "Signals API",
		"version": "1.0.0",
		"endpoints": [
			"/getTableBacktest",
			"/getTableAnalyst",
			"/getTradesBySignal/{signal_id}",
			"/admin/delete-signal/{signal_id}",
			"/admin/statistics",
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
