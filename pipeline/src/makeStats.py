from dataBaseModels import Backtest, Signal, Trade
from dataBaseModels import get_session, close_session
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import sys
from pathlib import Path
from logger_setup import get_logger

logger = get_logger(__name__)
output_dir = Path(__file__).parent / "output"
config_dir = Path(__file__).parent / "config"

def main(
		listTimeFrame: dict,
		listStrategy: dict,
		listSymbol: dict,
		listFactor: dict,
	) -> None:

	def rsplit_to_parts(s: str) -> list[str]:
		parts = s.rsplit('_', 4)
		return (parts + [None] * 5)[:5]

	listStrategy = [item.split(':')[0] for item in listStrategy]

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

	newTableBacktest = []
	for table in tableBacktest:
		splitStrategy = table["strategy"].rsplit('_', 4)
		realNameStrategy = splitStrategy[0].split(':')[0]

		try:
			splitFactor = splitStrategy[0].split(':')[1]
		except Exception as e:
			splitFactor = 'Fail'

		if (
				(splitStrategy[2] in listTimeFrame) and
				(splitStrategy[1] in listSymbol) and
				(realNameStrategy in listStrategy) and
				(
					splitFactor == 'Fail' or
					(splitFactor in listFactor)
				)
			):
			newTableBacktest.append({
				"id": table["id"],
				"strategy": table["strategy"],
				"year_profit": table["year_profit"] if table["year_profit"] > -100 else -100,
				"max_drawdown": table["max_drawdown"],
				"sharp": table["sharp"] if table["sharp"] > -1 else -1,
				"datetime": table["datetime"]
			})
	dataframe = pl.from_dicts(newTableBacktest)

	dataframe = dataframe.with_columns([
		pl.col("strategy")
		  .map_elements(rsplit_to_parts, return_dtype=pl.List(pl.Utf8))
		  .alias("parts")
	]).with_columns([
		pl.col("parts").list.get(0).alias("strategy_name"),
		pl.col("parts").list.get(1).alias("symbol"),
		pl.col("parts").list.get(2).alias("timeframe"),
		pl.col("parts").list.get(3).alias("strategy_type"),
		pl.col("parts").list.get(4).alias("exchange"),
	]).drop("parts")

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

			base = (
				dataframe.group_by([nameY, nameX])
				.agg(pl.col(metric_name)
				.mean().alias(metric_name))
			)
			pivot = (
				base.pivot(
					values=metric_name,
					index=nameY,
					columns=nameX,
					aggregate_function="first"
				)
			)

			cols = [c for c in pivot.columns if c != nameY]
			sorted_cols = sort_cols_and_rows(cols, nameX)
			pivot = pivot.select([nameY] + sorted_cols)

			cols = [c for c in pivot.columns if c != nameY]
			pivot = pivot.with_columns(pl.concat_list(cols).list.mean().alias("final_mean"))

			cols = [c for c in pivot.columns if c not in (nameY, "final_mean")]
			col_means = pivot.select([pl.col(c).mean().alias(c) for c in cols]).row(0)
			overall_mean = pivot.select(pl.col("final_mean").mean()).item()
			final_row = {nameY: "final_mean", **{c: col_means[i] for i, c in enumerate(cols)}, "final_mean": overall_mean}
			pivot = pl.concat([pivot, pl.DataFrame([final_row])], how="vertical")

			cols = [c for c in pivot.columns if c != nameY]
			y_labels = pivot.select(nameY).to_series().to_list()
			y_labels = [str(x) for x in y_labels]
			x_labels = [str(c) for c in cols]
			heat = pivot.select(cols).to_numpy()
			heat = np.array(heat, dtype=float)

			fig, ax = plt.subplots(figsize=(12, 8))
			sns.heatmap(
				heat,
				ax=ax,
				xticklabels=x_labels,
				yticklabels=y_labels,
				annot=True,
				fmt=".2f",
				cmap="RdYlGn",
				center=0,
				robust=True,
				linewidths=0.5,
				linecolor="white",
				cbar_kws={"shrink": 0.8, "label": metric_name.replace("_", " ").title()},
				square=False,
			)

			ax.set_xlabel(nameX)
			ax.set_ylabel(nameY)
			ax.set_title(metric_name, fontsize=16, fontweight="bold", pad=20)

			plt.xticks(rotation=45, ha="right")
			plt.yticks(rotation=0)
			plt.tight_layout()

			fileName: str = f'{output_dir}/stats_{nameY}_{nameX}_{metric_name}.png'
			plt.savefig(fileName, dpi=300, bbox_inches="tight", facecolor="white")
			plt.close()

			logger.info(f"pivot {nameY}_{nameX}_{metric_name} is save to {fileName}")

def sort_cols_and_rows(inputList, name):

	if name == 'timeframe':
		priority: dict = {
			'1min': 1,
			'2min': 2,
			'4min': 4,
			'5min': 5,
			'6min': 6,
			'8min': 8,
			'9min': 9,
			'10min': 10,
			'12min': 12,
			'15min': 15,
			'16min': 16,
			'18min': 18,
			'20min': 20,
			'24min': 24,
			'25min': 25,
			'30min': 30,
			'32min': 32,
			'36min': 36,
			'40min': 40,
			'45min': 45,
			'48min': 48,
			'50min': 50,
			'1h': 60,
			'2h': 120,
			'3h': 180,
			'4h': 240,
			'6h': 360,
			'8h': 480,
			'12h': 720,
			'1d': 1440
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