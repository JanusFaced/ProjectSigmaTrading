from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dataBaseModels import Backtest, Signal, Trade
from dataBaseModels import get_session, close_session
import os
from logger_setup import get_logger

logger = get_logger(__name__)

MODE_WORK = os.getenv('MODE_WORK')

if MODE_WORK == 'localhost':
	allow_origins = ['*']
elif MODE_WORK == 'server':
	allow_origins = [
		"https://projectsigmatrading.ru",
		"http://projectsigmatrading.ru",
		"https://62.113.37.47",
		"http://62.113.37.47"
	]

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
		signals = dataBaseSession.query(Signal).all()
		
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
async def get_trades_by_signal(signal_id: int):
	dataBaseSession = get_session()
	
	try:
		logger.info(f"Fetching trades for signal ID: {signal_id}")
		
		signal = dataBaseSession.query(Signal).filter(Signal.id == signal_id).first()
		if not signal:
			logger.warning(f"Signal with ID {signal_id} not found")
			raise HTTPException(status_code=404, detail="Signal not found")
		
		trades = dataBaseSession.query(Trade).filter(Trade.signal_id == signal_id).order_by(Trade.datetime).all()
		
		tradesData = []
		for trade in trades:
			tradesData.append({
				"id": trade.id,
				"deposit": str(round(trade.deposit, 2)),
				"datetime": str(trade.datetime.strftime("%Y-%m-%d %H:%M")) if trade.datetime else "N/A"
			})
		
		if trades:
			total_trades = len(trades)
		else:
			total_trades = 0
		
		logger.info(f"Successfully fetched {len(tradesData)} trades for signal {signal_id}")
		
		return {
			"strategy": signal.strategy,
			"trades": tradesData,
			"statistics": {
				"total_trades": total_trades
			}
		}
	
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error fetching trades for signal {signal_id}: {str(e)}")
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
