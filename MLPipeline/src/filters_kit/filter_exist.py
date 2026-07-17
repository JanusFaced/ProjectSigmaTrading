import json
import os
from pathlib import Path
from logger_setup import get_logger

logger = get_logger(__name__)
output_dir = Path(__file__).parent.parent / "output"
config_dir = Path(__file__).parent.parent / "config"

def main(listMSGs: dict, target_year_profit: float = 0.0) -> dict:
	fileName: str = f'{config_dir}/work_strats.json'
	with open(fileName, 'r', encoding='utf-8') as f:
		saveListMSGs = json.load(f)
	logger.info(f"📂 Загружено {len(saveListMSGs)} стратегий из файла")

	newListMSGs = []
	for msg in listMSGs:
		for save in saveListMSGs:
			if (
					(msg["strategy"] == save["strategy"]) and
					(msg["symbol"] == save["symbol"]) and
					(msg["timeFrame"] == save["timeFrame"]) and
					(msg["type"] == save["type"]) and
					(msg["nameExchange"] == save["nameExchange"]) and
					(msg["factor"] == save["factor"]) and
					(msg["typeFactor"] == save["typeFactor"]) and
					(msg["factorExchange"] == save["factorExchange"])
				):
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

	return newListMSGs