from flask import Flask, jsonify, request
from flask_cors import CORS
from dataBaseModels import Session, Signal
from sqlalchemy import desc
from pathlib import Path
import os
import sys
import logging
import make_logger

current_file_path = Path(__file__).resolve()
current_dir = current_file_path.parent
os.environ['LEVEL_CONFIG'] = 'INFO'
os.environ['WAY_TO_LOG_JOURNAL'] = str(current_dir/'logs'/'log_journal.log')
os.environ['WAY_EXTRACT_FILES'] = str(current_dir/'extract_files')

make_logger.make()
logger = logging.getLogger('DATAMINER:dms')

app = Flask(__name__)
CORS(app)

@app.route('/getTableAnalyst', methods=['GET'])
def getTableAnalyst():
    dataBaseSession = Session()

    try:
        signals = dataBaseSession.query(Signal).all()
        
        tableAnalyst = []
        for signal in signals:
            tableAnalyst.append({
                "id": signal.id,
                "asset": signal.asset,
                "ml_model": signal.ml_model,
                "timeframe": signal.timeframe,
                "accuracy": signal.accuracy,
                "signal": signal.signal
            })
        
        return jsonify(tableAnalyst)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        dataBaseSession.close()