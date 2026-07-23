import duckdb
import os
from logger_setup import get_logger

logger = get_logger(__name__)

_db = None

def get_duckdb():
	global _db
	if _db is None:
		_db = duckdb.connect()
		_db.execute(f"""
			INSTALL postgres;
			LOAD postgres;
			ATTACH 'host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT')}
					dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')}
					password={os.getenv('DB_PASSWORD')}' AS pg (TYPE postgres);
		""")
		logger.info("DuckDB подключен и приаттачен к PostgreSQL")
	return _db

def close_duckdb():
	global _db
	if _db:
		_db.execute("DROP TABLE IF EXISTS temp_analyst")
		_db.execute("DROP TABLE IF EXISTS temp_trading")
		_db.close()
		_db = None
		logger.info("DuckDB закрыт, временные таблицы удалены")