from typing import Optional, Any
import logging
import sys

class LoggerSetup:
    _initialized: bool = False
    _loggers: dict[str, Any] = {}
    
    @classmethod
    def configure(cls, 
            log_level: str = "INFO"
        ):

        if cls._initialized:
            return
            
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(console_handler)
        
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
