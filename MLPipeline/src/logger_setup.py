from typing import Optional, Any
import logging
import logging.config
import json
import os
from pathlib import Path
from concurrent_log_handler import ConcurrentRotatingFileHandler

class LoggerSetup:
	_initialized: bool = False
	_loggers: dict[str, Any] = {}
	
	@classmethod
	def configure(cls, 
			config_path: Optional[Path] = None,
			log_level: str = "INFO",
			log_dir: Optional[Path] = None
		):

		if cls._initialized:
			return
			
		if config_path and config_path.exists():
			with open(config_path, 'r') as f:
				config = json.load(f)
			logging.config.dictConfig(config)
		else:
			if log_dir is None:
				log_dir = Path(__file__).parent.parent / "logs"
			log_dir.mkdir(exist_ok=True)
			
			log_file = log_dir / "app.log"
			
			handlers = {
				'console': {
					'class': 'logging.StreamHandler',
					'level': log_level,
					'formatter': 'detailed',
					'stream': 'ext://sys.stdout'
				},
				'file': {
					'()': ConcurrentRotatingFileHandler,
					'filename': str(log_file),
					'maxBytes': 10485760,
					'backupCount': 3,
					'encoding': 'utf-8',
					'use_gzip': True,
					'level': log_level,
					'formatter': 'detailed'
				}
			}
			
			logging_config = {
				'version': 1,
				'disable_existing_loggers': False,
				'formatters': {
					'detailed': {
						'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
					},
					'simple': {
						'format': '%(asctime)s - %(levelname)s - %(message)s'
					}
				},
				'handlers': handlers,
				'root': {
					'level': log_level,
					'handlers': list(handlers.keys())
				}
			}
			
			logging.config.dictConfig(logging_config)
		
		cls._initialized = True
	
	@classmethod
	def get_logger(cls, name: str, module_path: Optional[str] = None) -> logging.Logger:
		if not cls._initialized:
			cls.configure()
		
		logger_name = name
		if module_path:
			logger_name = f"{module_path}.{name}"
		
		return logging.getLogger(logger_name)

def get_logger(name: str) -> logging.Logger:
	return LoggerSetup.get_logger(name)