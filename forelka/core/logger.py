"""
Logging configuration for Forelka Userbot
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional


class TerminalLogger:
    """Custom logger that writes to both terminal and file"""
    
    def __init__(self, log_file: str = "forelka.log", level: str = "INFO"):
        self.log_file = log_file
        self.level = level
        self.ignore_list = [
            "PERSISTENT_TIMESTAMP_OUTDATED",
            "updates.GetChannelDifference",
            "RPC_CALL_FAIL",
            "Retrying \"updates.GetChannelDifference\"",
            "disable_web_page_preview"
        ]
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, self.level))
        file_handler.setFormatter(formatter)
        
        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.level))
        console_handler.setFormatter(formatter)
        
        # Setup logger
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, self.level))
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Redirect stdout/stderr to our logger
        sys.stdout = self
        sys.stderr = self
    
    def write(self, message: str):
        """Write message to log"""
        if not message.strip():
            return
        
        # Check if message should be ignored
        if any(x in message for x in self.ignore_list):
            return
        
        # Write to original terminal
        sys.__stdout__.write(message)
        
        # Write to log file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(message)
    
    def flush(self):
        """Flush output"""
        sys.__stdout__.flush()
    
    def __getattr__(self, name):
        """Delegate other attributes to original stdout"""
        return getattr(sys.__stdout__, name)


def setup_logger(level: str = "INFO", log_file: str = "forelka.log"):
    """Setup logging for the application"""
    TerminalLogger(log_file, level)
    
    # Suppress some verbose logs
    logging.getLogger("pyrogram").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("🚀 Forelka Userbot logging initialized")
    logger.info(f"📁 Log file: {log_file}")
    logger.info(f"📊 Log level: {level}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


def log_startup_info():
    """Log startup information"""
    logger = logging.getLogger(__name__)
    
    import platform
    import sys
    
    logger.info("=" * 50)
    logger.info("🚀 Forelka Userbot Startup")
    logger.info(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"💻 Platform: {platform.platform()}")
    logger.info(f"🐍 Python: {sys.version}")
    logger.info(f"📦 Working directory: {os.getcwd()}")
    logger.info("=" * 50)