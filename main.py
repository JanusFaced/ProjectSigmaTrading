from datetime import datetime, timedelta, timezone
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import os
import sys
import logging
import make_logger
import json
import requests

current_file_path = Path(__file__).resolve()
current_dir = current_file_path.parent

os.environ['LEVEL_CONFIG'] = 'INFO'
os.environ['WAY_TO_LOG_JOURNAL'] = str(current_dir/'logs'/'log_journal.log')
os.environ['WAY_EXTRACT_FILES'] = str(current_dir/'extract_files')

make_logger.make()
logger = logging.getLogger('DATAMINER:dms')

def main():

	for _ in range(10):
		logger.info('Hello, world!')

try:
	main()

except Exception as error_body:
	logger.critical('Critical error!!!', exc_info=True)

