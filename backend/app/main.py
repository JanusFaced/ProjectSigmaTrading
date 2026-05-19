from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import os
import sys
import logging
import make_logger

import data

current_file_path = Path(__file__).resolve()
current_dir = current_file_path.parent
os.environ['LEVEL_CONFIG'] = 'INFO'
os.environ['WAY_TO_LOG_JOURNAL'] = str(current_dir/'logs'/'log_journal.log')
os.environ['WAY_EXTRACT_FILES'] = str(current_dir/'extract_files')

make_logger.make()
logger = logging.getLogger('DATAMINER:dms')

app = Flask(__name__)
CORS(app)

tableAnalyst = data.main()

@app.route('/getTableAnalyst', methods=['GET'])
def getTableAnalyst():
    return jsonify(tableAnalyst)