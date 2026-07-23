from dataBaseModels import Backtest, Signal, Trade
from dataBaseModels import get_session, close_session
import json
import os
from pathlib import Path
from logger_setup import get_logger

logger = get_logger(__name__)
output_dir = Path(__file__).parent.parent / "output"
config_dir = Path(__file__).parent.parent / "config"

def main(listMSGs: dict, target_year_profit: float = 0.0) -> dict:
	
	fileName: str = f'{config_dir}/work_strats.json'
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
	
	except Exception as e:
		logger.error(f"Error fetching backtests: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))
	
	finally:
		close_session()

	newListMSGs = []
	for msg in listMSGs:
		
		msg_strategy = msg["strategy"]

		splitNameStrategy = msg_strategy.split(":")
		firstName = splitNameStrategy[0]
		lastName = splitNameStrategy[1]

		if lastName == 'I':
			msg_strategy = firstName

		elif lastName == 'II':
			msg_strategy = ":".join([
				firstName,
				msg['factor'],
				msg['typeFactor'],
				msg['factorExchange']
			])

		msg_symbol = msg["symbol"]
		msg_timeFrame = msg["timeFrame"]
		msg_type = msg["type"]
		msg_nameExchange = msg["nameExchange"]

		nameStrategy = f"{msg_strategy}_{msg_symbol}_{msg_timeFrame}_{msg_type}_{msg_nameExchange}"

		for table in tableBacktest:
			if (nameStrategy == table['strategy']) and (table['year_profit'] > target_year_profit):

				newListMSGs.append({
					'mode': msg["mode"],
					'nameExchange': msg["nameExchange"],
					'symbol': msg["symbol"],
					'type': msg["type"],
					'timeFrame': msg["timeFrame"],
					'strategy': msg["strategy"],
					'factor': msg["factor"],
					'typeFactor': msg["typeFactor"],
					'factorExchange': msg["factorExchange"]
				})

	with open(fileName, 'w', encoding='utf-8') as f:
		json.dump(newListMSGs, f, indent=4, ensure_ascii=False)
	logger.info(f"{fileName} save!")
	return newListMSGs