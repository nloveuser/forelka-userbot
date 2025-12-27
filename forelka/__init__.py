"""
Forelka Userbot - A modular Telegram userbot with multi-account support
"""

__version__ = "2.0.0"
__author__ = "Kirillusha"
__description__ = "A modular Telegram userbot with multi-account support and web interface"

from .core.bot import ForelkaBot
from .core.database import DatabaseManager
from .core.config import ConfigManager
from .core.module_loader import ModuleLoader
from .core.command_handler import CommandHandler
from .core.logger import setup_logger

__all__ = [
    'ForelkaBot',
    'DatabaseManager', 
    'ConfigManager',
    'ModuleLoader',
    'CommandHandler',
    'setup_logger'
]