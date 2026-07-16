from typing import Any
import polars as pl
import os
from convertorTF import convertorTimeFrame
from custom_ta import adaptive_volume, adaptive_modeling_volume, adaptive_roc
from pathlib import Path
from duckDB_setup import get_duckdb
from logger_setup import get_logger

logger = get_logger(__name__)
output_dir = Path(__file__).parent.parent / "output"

def main(inputMessage: dict[str, Any]) -> None:
	db = get_duckdb()
	dataFrame = db.execute("""
		SELECT 
			datetime,
			CAST(open AS FLOAT) AS open,
			CAST(high AS FLOAT) AS high,
			CAST(low AS FLOAT) AS low,
			CAST(close AS FLOAT) AS close,
			CAST(volume AS BIGINT) AS volume
		FROM temp_analyst 
		ORDER BY datetime
	""").pl()
	db.execute("DROP TABLE IF EXISTS temp_analyst")

	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']
	strategy = inputMessage['strategy']

	volativityWindow = 200
	signalWindow = 20
	trendWindow = 200
	maxMulti = 15
	minMulti = 1
	baseVolativity1m = 0.0004
	baseVolativity = baseVolativity1m*convertorTimeFrame(timeFrame)

	dataFrame = dataFrame.with_columns((pl.col('close')/pl.col('close').shift(1) - 1).abs().cast(pl.Float32).alias('diff'))
	dataFrame = dataFrame.with_columns(pl.col('diff').rolling_mean(window_size=volativityWindow).cast(pl.Float32).alias('volativity'))
	dataFrame = dataFrame.with_columns((pl.lit(baseVolativity)/pl.col('volativity')).cast(pl.Int16).alias('window'))

	dataFrame = dataFrame.with_columns([
		(pl.col('window')*signalWindow).fill_null(signalWindow).cast(pl.Int16).clip(2, None).alias('signalWindow'),
		(pl.col('window')*trendWindow).fill_null(trendWindow).cast(pl.Int16).clip(2, None).alias('trendWindow'),
	])

	signal_diff = adaptive_roc(
		closeVector=dataFrame['close'].to_numpy(),
		windowVector=dataFrame['signalWindow'].to_numpy()
	)
	original = abs(signal_diff)
	primary = adaptive_volume(
		volumeVector=dataFrame['volume'].to_numpy(),
		windowVector=dataFrame['signalWindow'].to_numpy()
	)

	p_model, n_model = adaptive_modeling_volume(
		secondaryVector=original,
		primaryVector=primary,
		windowVector=dataFrame['signalWindow'].to_numpy()
	)

	trend = adaptive_roc(
		closeVector=dataFrame['close'].to_numpy(),
		windowVector=dataFrame['trendWindow'].to_numpy()
	)

	dataFrame = dataFrame.with_columns([
		pl.Series('signal_diff', signal_diff),
		pl.Series('p_model', p_model),
		pl.Series('n_model', n_model),
		pl.Series('trend', trend),
	])

	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('signal_diff') > pl.col('n_model')) &
			(pl.col('trend') > 0) &
			(pl.col('window') < maxMulti) &
			(pl.col('window') > minMulti)
		).then(pl.lit(2, dtype=pl.Int8))
		.when(
			(pl.col('signal_diff') < pl.col('p_model')) &
			(pl.col('trend') < 0) &
			(pl.col('window') < maxMulti) &
			(pl.col('window') > minMulti)
		).then(pl.lit(0, dtype=pl.Int8))
		.otherwise(pl.lit(1, dtype=pl.Int8))
		.alias('strategy')
	)
	
	dataFrame = dataFrame.with_columns([
		pl.when(pl.col('strategy') == 2).then(pl.lit(-1, dtype=pl.Int8)).otherwise(pl.lit(1, dtype=pl.Int8)).alias('long_signal'),
		pl.when(pl.col('strategy') == 0).then(pl.lit(1, dtype=pl.Int8)).otherwise(pl.lit(-1, dtype=pl.Int8)).alias('short_signal'),
	])

	dataFrame = dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal'])
	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")
