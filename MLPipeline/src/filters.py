from dataBaseModels import Session, Backtest, Signal, Trade
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from pathlib import Path
from logger_setup import get_logger

logger = get_logger(__name__)
output_dir = Path(__file__).parent / "output"

def sort_cols_and_rows(inputList, name):

	if name == 'timeframe':
		priority = {
			'1min': 1,
			'2min': 2,
			'4min': 4,
			'8min': 8,
			'15min': 15,
			'30min': 30,
			'1h': 60,
			'2h': 120,
			'4h': 240,
			'6h': 360,
			'8h': 480,
		   '12h': 720,
			'1d': 1440,
		}
		outputList = sorted(inputList, key=lambda x: priority.get(str(x), 9999))
	
	elif name == 'symbol':
		priority = {
			'BTC': 1,
			'ETH': 2,
			'BNB': 3,
			'XRP': 4,
			'SOL': 5,
			'TRX': 6,
			'HYPE': 7,
			'ADA': 8,
			'LINK': 9,
		}
		outputList = sorted(inputList, key=lambda x: priority.get(str(x), 9999))
	
	else:
		outputList = inputList

	return outputList

def makeStats(listSymbol: dict, listTimeFrame: dict, listStrategy: dict) -> None:
	dataBaseSession = Session()

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
		dataBaseSession.close()

	newTableBacktest = []
	for table in tableBacktest:
		splitStrategy = table["strategy"].rsplit('_', 4)
		if (splitStrategy[2] in listTimeFrame) and (splitStrategy[1] in listSymbol) and (splitStrategy[0] in listStrategy):
			newTableBacktest.append({
				"id": table["id"],
				"strategy": table["strategy"],
				"year_profit": table["year_profit"] if table["year_profit"] > -100 else -100,
				"max_drawdown": table["max_drawdown"],
				"sharp": table["sharp"] if table["sharp"] > -1 else -1,
				"datetime": table["datetime"]
			})
	dataframe = pd.DataFrame(newTableBacktest)

	split_parts = dataframe['strategy'].str.rsplit('_', n=4, expand=True)
	
	dataframe['strategy_name'] = split_parts[0]
	dataframe['symbol'] = split_parts[1]
	dataframe['timeframe'] = split_parts[2]
	dataframe['strategy_type'] = split_parts[3]
	dataframe['exchange'] = split_parts[4]

	list_of_combi = [
		['strategy_name', 'timeframe'],
		['strategy_name', 'symbol'],
		['symbol', 'timeframe']
	]
	list_of_metrics = ['year_profit']

	for combi in list_of_combi:
		for metric_name in list_of_metrics:
			nameY = combi[0]
			nameX = combi[1]

			pivot = pd.pivot_table(
				dataframe,
				values=metric_name,
				index=nameY,
				columns=nameX,
				aggfunc='mean',
				margins=True,
				margins_name='final_mean'
			)

			cols = [col for col in pivot.columns if col != 'final_mean']
			sorted_cols = sort_cols_and_rows(cols, nameX)
			pivot = pivot[sorted_cols + ['final_mean']]

			rows = [row for row in pivot.index if row != 'final_mean']
			sorted_rows = sort_cols_and_rows(rows, nameY)
			pivot = pivot.reindex(sorted_rows + ['final_mean'])

			fig, ax = plt.subplots(figsize=(12, 8))
			sns.heatmap(
				pivot,
				annot=True,
				fmt='.2f',
				cmap='RdYlGn',
				center=0,
				robust=True,
				square=False,
				linewidths=0.5,
				linecolor='white',
				cbar_kws={'shrink': 0.8, 'label': metric_name.replace('_', ' ').title()},
				ax=ax
			)
			ax.set_title(f'{metric_name}', fontsize=16, fontweight='bold', pad=20)
			ax.set_xlabel(nameX, fontsize=12)
			ax.set_ylabel(nameY, fontsize=12)
			plt.xticks(rotation=45, ha='right')
			plt.yticks(rotation=0)
			plt.tight_layout()
			fileName: str = f'{output_dir}/stats_{nameY}_{nameX}_{metric_name}.png'
			plt.savefig(fileName, dpi=300, bbox_inches='tight', facecolor='white')
			plt.close()

			logger.info(f"pivot {nameY}_{nameX}_{metric_name} is save to {fileName}")

def forImitation(listMSGs: dict, target_year_profit: float = 0.0) -> dict:

	dataBaseSession = Session()

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
		dataBaseSession.close()

	newListMSGs = []
	for msg in listMSGs:
		
		msg_strategy = msg["strategy"]
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
					'strategy': msg["strategy"]
				})

	return newListMSGs

def forReal(listMSGs: dict, target_year_profit: float = 0.0) -> dict:
	return listMSGs