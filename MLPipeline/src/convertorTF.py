import os
import sys
from logger_setup import get_logger

logger = get_logger(__name__)

def convertorTimeFrame(timeFrame: str) -> int:

	convertor: dict = {
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
		'4h': 240,
		'6h': 360,
		'8h': 480,
		'12h': 720,
		'1d': 1440
	}

	return convertor[timeFrame]