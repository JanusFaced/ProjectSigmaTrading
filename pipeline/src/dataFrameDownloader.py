from typing import Literal, Any
from datetime import datetime, timedelta
import os
import re
from convertorTF import convertorTimeFrame
from duckDB_setup import get_duckdb
from logger_setup import get_logger

logger = get_logger(__name__)

def main(
		nameExchange: str,
		symbol: str,
		type: str,
		timeFrame: str,
		mode: str,
		factor: str,
		typeFactor: str,
		factorExchange: str
	) -> None:

	db = get_duckdb()
	base_table = _load_data(db, nameExchange, symbol, type, timeFrame, mode)
	
	if factor == 'None':
		result_table = _resample(db, base_table, timeFrame, factor_mode=False)
	else:
		factor_table = _load_data(db, factorExchange, factor, typeFactor, timeFrame, mode)
		merged_table = _merge_tables(db, base_table, factor_table)
		result_table = _resample(db, merged_table, timeFrame, factor_mode=True)
		db.execute(f"DROP TABLE IF EXISTS {factor_table}")
		db.execute(f"DROP TABLE IF EXISTS {merged_table}")
	
	db.execute(f"CREATE OR REPLACE TEMP TABLE temp_analyst AS SELECT * FROM {result_table}")
	logger.info(f"Данные подготовлены, сохранены в temp_analyst")
	db.execute(f"DROP TABLE IF EXISTS {base_table}")
	db.execute(f"DROP TABLE IF EXISTS {result_table}")

def _load_data(
		db,
		nameExchange: str,
		symbol: str,
		type: str,
		timeFrame: str,
		mode: str
	) -> str:

	valueConvertor = convertorTimeFrame(timeFrame)

	if mode == 'test':
		nowMuchMoreDays: int = 9999
		maxDelta = 30
		maxDeltaDatetime = timedelta(days=maxDelta)
		speedOfTest = 'slow'
		
		if speedOfTest == 'fast':
			modeMultiple, standartDeep = "relative", 5_000
		elif speedOfTest == 'slow':
			modeMultiple, standartDeep = "identical", 5_000_000
		
		if modeMultiple == "identical":
			realAmountLines: int = standartDeep
		elif modeMultiple == "relative":
			realAmountLines: int = standartDeep*valueConvertor
		
		nameTable = f"{nameExchange}_{symbol}_{type}".lower()

	else:
		nowMuchMoreDays: int = 125
		maxDeltaDatetime = timedelta(minutes=valueConvertor)
		standartDeep = 3000
		realAmountLines = standartDeep*valueConvertor
		nameTable = f"short_{nameExchange}_{symbol}_{type}".lower()
			
	last_date = db.execute(f"SELECT MAX(datetime) FROM pg.{nameTable}").fetchone()[0]
	approx_start_date = last_date - timedelta(minutes=realAmountLines)
	
	if approx_start_date.time() != datetime.min.time():
		start_date = (approx_start_date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
	else:
		start_date = approx_start_date
	
	logger.info(f"Загружаем данные с {start_date} (исходно было ~{approx_start_date})")
	
	temp_table = f"temp_{nameExchange}_{symbol}_{type}"
	
	db.execute(f"""
		CREATE OR REPLACE TEMP TABLE {temp_table} AS
		SELECT * FROM (
			SELECT * FROM pg.{nameTable}
			WHERE datetime >= '{start_date}'
			ORDER BY datetime DESC
			LIMIT {realAmountLines}
		) AS last_rows
		ORDER BY datetime ASC
	""")
	
	return temp_table

def _resample(
		db,
		input_table: str,
		timeframe: str,
		factor_mode: bool = False
	) -> str:
	def to_interval(tf: str) -> str:
		tf = tf.lower().strip()
		int_tf = int(re.search(r'\d+', tf).group())
		if tf.endswith('min'):
			return f"INTERVAL '{int_tf}' MINUTE"
		elif tf.endswith('h'):
			return f"INTERVAL '{int_tf}' HOUR"
		elif tf.endswith('d'):
			return f"INTERVAL '{int_tf}' DAY"
		else:
			raise ValueError(f"Unsupported timeframe: {tf}")
	output_table = "resampled"
	if factor_mode:
		agg_columns = """
			FIRST(open) AS open,
			MAX(high) AS high,
			MIN(low) AS low,
			LAST(close) AS close,
			SUM(volume) AS volume,
			FIRST(openFactor) AS openFactor,
			MAX(highFactor) AS highFactor,
			MIN(lowFactor) AS lowFactor,
			LAST(closeFactor) AS closeFactor,
			SUM(volumeFactor) AS volumeFactor
		"""
	else:
		agg_columns = """
			FIRST(open) AS open,
			MAX(high) AS high,
			MIN(low) AS low,
			LAST(close) AS close,
			SUM(volume) AS volume
		"""
	interval = to_interval(timeframe)
	db.execute(f"""
		CREATE OR REPLACE TEMP TABLE {output_table} AS
		SELECT 
			time_bucket({interval}, datetime) AS datetime,
			{agg_columns}
		FROM {input_table}
		GROUP BY time_bucket({interval}, datetime)
		ORDER BY datetime
	""")
	db.execute(f"""
		DELETE FROM {output_table} 
		WHERE datetime = (SELECT MAX(datetime) FROM {output_table})
	""")
	return output_table

def _merge_tables(db, base_table: str, factor_table: str) -> str:
	output_table = "merged"
	db.execute(f"""
		CREATE OR REPLACE TEMP TABLE factor_renamed AS
		SELECT 
			datetime,
			open AS openFactor,
			high AS highFactor,
			low AS lowFactor,
			close AS closeFactor,
			volume AS volumeFactor
		FROM {factor_table}
	""")
	db.execute(f"""
		CREATE OR REPLACE TEMP TABLE {output_table} AS
		SELECT 
			base.datetime,
			base.open,
			base.high,
			base.low,
			base.close,
			base.volume,
			factor.openFactor,
			factor.highFactor,
			factor.lowFactor,
			factor.closeFactor,
			factor.volumeFactor
		FROM {base_table} base
		INNER JOIN factor_renamed factor ON base.datetime = factor.datetime
		ORDER BY base.datetime
	""")
	db.execute("DROP TABLE IF EXISTS factor_renamed")
	return output_table