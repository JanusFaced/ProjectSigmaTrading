import polars as pl
import dataFrameDownloader
from strategies import (
	trend_cross_hama,
	trend_cross_hama_x2,
	trend_cross_hama_x3,
	trend_roc,
	trend_roc_x2,
	trend_roc_x3,
	trend_envelopes,
	trend_envelopes_x2,
	trend_envelopes_x3,
	trend_pattern_soldiers,
	trend_pattern_soldiers_x2,
	trend_pattern_soldiers_x3,
	trend_zigzag_pinbar,
	trend_zigzag_pinbar_x2,
	trend_zigzag_pinbar_x3,
	trend_zzchannel_pinbar,
	trend_zzchannel_pinbar_x2,
	trend_zzchannel_pinbar_x3,
	line_hama,
	line_hama_x2,
	line_hama_x3,
	contr_roc,
	contr_roc_x2,
	contr_roc_x3,
	contr_envelopes,
	contr_envelopes_x2,
	contr_envelopes_x3,
	contr_hamacd,
	contr_hamacd_x2,
	contr_hamacd_x3,
	contr_pattern_star,
	contr_pattern_star_x2,
	contr_pattern_star_x3,
	corr_regression,
	corr_regression_x2,
	corr_regression_x3,
	corr_pirson,
	corr_pirson_x2,
	corr_pirson_x3,
)
import trading_simulator
import imitation_connector
from duckDB_setup import close_duckdb
from logger_setup import get_logger

logger = get_logger(__name__)

def main(inputMessage: dict) -> None:
	nameStrategy = inputMessage["strategy"]
	splitNameStrategy = nameStrategy.split(":")
	firstName = splitNameStrategy[0]
	lastName = splitNameStrategy[1]

	if lastName == 'I':
		inputMessage['strategy'] = firstName

	elif lastName == 'II':
		inputMessage['strategy'] = ":".join([
			firstName,
			inputMessage['factor'],
			inputMessage['typeFactor'],
			inputMessage['factorExchange']
		])
	
	dataFrameDownloader.main(
		nameExchange=inputMessage['nameExchange'],
		symbol=inputMessage['symbol'],
		type=inputMessage['type'],
		timeFrame=inputMessage['timeFrame'],
		mode=inputMessage['mode'],
		factor=inputMessage['factor'],
		typeFactor=inputMessage['typeFactor'],
		factorExchange=inputMessage['factorExchange']
	)

	if firstName == "trend_cross_hama":
		trend_cross_hama.main(inputMessage)
	elif firstName == "trend_cross_hama_x2":
		trend_cross_hama_x2.main(inputMessage)
	elif firstName == "trend_cross_hama_x3":
		trend_cross_hama_x3.main(inputMessage)
	elif firstName == "trend_roc":
		trend_roc.main(inputMessage)
	elif firstName == "trend_roc_x2":
		trend_roc_x2.main(inputMessage)
	elif firstName == "trend_roc_x3":
		trend_roc_x3.main(inputMessage)
	elif firstName == "trend_envelopes":
		trend_envelopes.main(inputMessage)
	elif firstName == "trend_envelopes_x2":
		trend_envelopes_x2.main(inputMessage)
	elif firstName == "trend_envelopes_x3":
		trend_envelopes_x3.main(inputMessage)
	elif firstName == "trend_pattern_soldiers":
		trend_pattern_soldiers.main(inputMessage)
	elif firstName == "trend_pattern_soldiers_x2":
		trend_pattern_soldiers_x2.main(inputMessage)
	elif firstName == "trend_pattern_soldiers_x3":
		trend_pattern_soldiers_x3.main(inputMessage)
	elif firstName == "trend_zigzag_pinbar":
		trend_zigzag_pinbar.main(inputMessage)
	elif firstName == "trend_zigzag_pinbar_x2":
		trend_zigzag_pinbar_x2.main(inputMessage)
	elif firstName == "trend_zigzag_pinbar_x3":
		trend_zigzag_pinbar_x3.main(inputMessage)
	elif firstName == "trend_zzchannel_pinbar":
		trend_zzchannel_pinbar.main(inputMessage)
	elif firstName == "trend_zzchannel_pinbar_x2":
		trend_zzchannel_pinbar_x2.main(inputMessage)
	elif firstName == "trend_zzchannel_pinbar_x3":
		trend_zzchannel_pinbar_x3.main(inputMessage)
	elif firstName == "line_hama":
		line_hama.main(inputMessage)
	elif firstName == "line_hama_x2":
		line_hama_x2.main(inputMessage)
	elif firstName == "line_hama_x3":
		line_hama_x3.main(inputMessage)
	elif firstName == "contr_roc":
		contr_roc.main(inputMessage)
	elif firstName == "contr_roc_x2":
		contr_roc_x2.main(inputMessage)
	elif firstName == "contr_roc_x3":
		contr_roc_x3.main(inputMessage)
	elif firstName == "contr_envelopes":
		contr_envelopes.main(inputMessage)
	elif firstName == "contr_envelopes_x2":
		contr_envelopes_x2.main(inputMessage)
	elif firstName == "contr_envelopes_x3":
		contr_envelopes_x3.main(inputMessage)
	elif firstName == "contr_hamacd":
		contr_hamacd.main(inputMessage)
	elif firstName == "contr_hamacd_x2":
		contr_hamacd_x2.main(inputMessage)
	elif firstName == "contr_hamacd_x3":
		contr_hamacd_x3.main(inputMessage)
	elif firstName == "contr_pattern_star":
		contr_pattern_star.main(inputMessage)
	elif firstName == "contr_pattern_star_x2":
		contr_pattern_star_x2.main(inputMessage)
	elif firstName == "contr_pattern_star_x3":
		contr_pattern_star_x3.main(inputMessage)


	elif firstName == "corr_regression":
		corr_regression.main(inputMessage)
	elif firstName == "corr_pirson":
		corr_pirson.main(inputMessage)
		
	if inputMessage['mode'] == 'test':
		trading_simulator.main(inputMessage)
	elif inputMessage['mode'] == 'imitation':
		imitation_connector.main(inputMessage)
	elif inputMessage['mode'] == 'real':
		pass

	close_duckdb()
