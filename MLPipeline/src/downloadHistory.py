from typing import Literal, Any
from datetime import datetime, timedelta
import duckdb
import ccxt
import os
from logger_setup import get_logger

logger = get_logger(__name__)

dataBase_password = os.getenv('DB_PASSWORD')
dataBase_user = os.getenv('DB_USER')
dataBase_name = os.getenv('DB_NAME')
dataBase_host = os.getenv('DB_HOST')
dataBase_port = os.getenv('DB_PORT')

def main(
		nameExchange: str,
		symbol: str,
		type: str,
		mode: str,
		nowMuchMoreDays: int
	) -> None:

	db = duckdb.connect()
	db.execute(f"""
		INSTALL postgres;
		LOAD postgres;
		ATTACH 'host={dataBase_host} port={dataBase_port} 
				dbname={dataBase_name} user={dataBase_user} 
				password={dataBase_password}' AS pg (TYPE postgres);
	""")

	if mode == 'test':
		nameTable = f"{nameExchange}_{symbol}_{type}".lower()
	elif mode in ['imitation', 'real']:
		nameTable = f"short_{nameExchange}_{symbol}_{type}".lower()
	else:
		raise ValueError(f"Неизвестный режим: {mode}")

	exchange = setExchange(nameExchange, type)
	ticker = f'{symbol}/USDT' if type == 'spot' else f'{symbol}/USDT:USDT'

	timeFrame = '1m'
	deltaDatetime = timedelta(minutes=1)
	limit = 1000

	try:
		result = db.execute(f"SELECT MAX(datetime) FROM pg.{nameTable}").fetchone()
		if result and result[0] is not None:
			initialDatetime = result[0] + deltaDatetime
			logger.info(f'{nameTable} exists! Last date: {result[0]}')
		else:
			raise Exception("Table is empty or doesn't exist")
	except Exception:
		logger.info(f'{nameTable} does NOT exist or is empty!')
		if mode == 'test':
			initialDatetime = datetime(2017, 1, 1)
		elif mode in ['imitation', 'real']:
			initialDatetime = datetime.utcnow() - timedelta(days=nowMuchMoreDays)

	logger.info(f'{nameTable} | Start parsing {symbol} from {initialDatetime}')
	collected = []
	while True:
		iso_string = initialDatetime.strftime('%Y-%m-%dT%H:%M:%SZ')
		since = exchange.parse8601(iso_string)
		ohlcv = exchange.fetch_ohlcv(ticker, timeFrame, since, limit)

		if not ohlcv:
			break

		for row in ohlcv:
			dt = datetime.utcfromtimestamp(row[0] / 1000)
			collected.append((dt, row[1], row[2], row[3], row[4], row[5]))

		last_dt = datetime.utcfromtimestamp(ohlcv[-1][0] / 1000)
		initialDatetime = last_dt + deltaDatetime
		nowDatetime = datetime.utcnow()

		logger.info(f"{nameTable} <=> {last_dt}")
		if initialDatetime >= nowDatetime:
			break

	if not collected:
		logger.info("Нет новых данных для загрузки")
		return

	logger.info(f"Собрано {len(collected)} свечей, начинаем обработку...")

	db.execute("CREATE OR REPLACE TEMP TABLE temp_raw (datetime TIMESTAMP, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE)")
	db.executemany("INSERT INTO temp_raw VALUES (?, ?, ?, ?, ?, ?)", collected)

	db.execute("""
		CREATE OR REPLACE TEMP TABLE temp_filled AS
		WITH all_minutes AS (
			SELECT UNNEST(generate_series(
				(SELECT MIN(datetime) FROM temp_raw),
				(SELECT MAX(datetime) FROM temp_raw),
				INTERVAL 1 MINUTE
			)) AS datetime
		),
		cleaned AS (
			SELECT DISTINCT ON (datetime) *
			FROM temp_raw
			ORDER BY datetime
		)
		SELECT 
			all_minutes.datetime,
			LAST_VALUE(cleaned.open IGNORE NULLS) OVER (ORDER BY all_minutes.datetime ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS open,
			LAST_VALUE(cleaned.high IGNORE NULLS) OVER (ORDER BY all_minutes.datetime ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS high,
			LAST_VALUE(cleaned.low IGNORE NULLS) OVER (ORDER BY all_minutes.datetime ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS low,
			LAST_VALUE(cleaned.close IGNORE NULLS) OVER (ORDER BY all_minutes.datetime ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS close,
			LAST_VALUE(cleaned.volume IGNORE NULLS) OVER (ORDER BY all_minutes.datetime ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS volume
		FROM all_minutes
		LEFT JOIN cleaned ON all_minutes.datetime = cleaned.datetime
		ORDER BY all_minutes.datetime
	""")

	db.execute(f"""
		CREATE TABLE IF NOT EXISTS pg.{nameTable} (
			datetime TIMESTAMP PRIMARY KEY,
			open DOUBLE,
			high DOUBLE,
			low DOUBLE,
			close DOUBLE,
			volume DOUBLE
		)
	""")

	db.execute(f"""
		INSERT INTO pg.{nameTable} (datetime, open, high, low, close, volume)
		SELECT datetime, open, high, low, close, volume
		FROM temp_filled
		WHERE NOT EXISTS (
			SELECT 1 FROM pg.{nameTable} 
			WHERE datetime = temp_filled.datetime
		)
	""")

	if mode in ['imitation', 'real']:
		cutoff_date = datetime.utcnow() - timedelta(days=nowMuchMoreDays)
		deleted = db.execute(f"""
			DELETE FROM pg.{nameTable}
			WHERE datetime < '{cutoff_date}'
		""")
		deleted_rows = deleted.fetchone()[0] if deleted else 0
		logger.info(f'Удалено {deleted_rows} старых записей (до {cutoff_date})')

	logger.info(f'{nameTable} успешно обновлён!')

def setExchange(nameExchange: str, type: str) -> ccxt.Exchange:
	if nameExchange == 'binance':
		exchange = ccxt.binance()
		if type == 'futures':
			exchange.options['defaultType'] = 'future'
	elif nameExchange == 'bybit':
		exchange = ccxt.bybit()
		if type == 'futures':
			exchange.options['defaultType'] = 'linear'
	elif nameExchange == 'kucoin':
		exchange = ccxt.kucoin()
		if type == 'futures':
			exchange.options['defaultType'] = 'future'
	else:
		raise ValueError(f"Неизвестная биржа: {nameExchange}")
	return exchange