"""
Utility functions for Forelka Userbot
"""

import os
import sys
import getpass
from typing import Optional


def check_root_warning():
    """Check if running as root and show warning"""
    if os.geteuid() == 0:  # Running as root
        print("⚠️  Warning: Running as root user!")
        print("It's recommended to run Forelka as a regular user for security reasons.")
        print("Use --root flag to skip this warning.")
        print()
        
        # Ask for confirmation unless --root was used
        response = input("Do you want to continue? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Exiting...")
            sys.exit(1)


def get_user_id_from_input() -> Optional[int]:
    """Get user ID from input with validation"""
    try:
        user_id = input("Enter your Telegram User ID: ").strip()
        return int(user_id)
    except ValueError:
        print("❌ Invalid User ID. Please enter a valid number.")
        return None


def get_api_credentials() -> tuple:
    """Get API credentials from user input"""
    api_id = input("Enter your API ID: ").strip()
    api_hash = input("Enter your API Hash: ").strip()
    return api_id, api_hash


def validate_telegram_credentials(api_id: str, api_hash: str) -> bool:
    """Validate Telegram API credentials"""
    if not api_id or not api_hash:
        return False
    
    try:
        int(api_id)
        return len(api_hash) == 32  # API hash should be 32 characters
    except ValueError:
        return False


def format_uptime(seconds: float) -> str:
    """Format uptime in a human-readable format"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    
    parts = []
    if d > 0:
        parts.append(f"{int(d)}д")
    if h > 0:
        parts.append(f"{int(h)}ч")
    if m > 0:
        parts.append(f"{int(m)}м")
    parts.append(f"{int(s)}с")
    
    return " ".join(parts)


def is_valid_prefix(prefix: str) -> bool:
    """Check if prefix is valid"""
    if not prefix or len(prefix) > 3:
        return False
    
    # Allow most characters except spaces and newlines
    return not any(c.isspace() for c in prefix)


def sanitize_module_name(name: str) -> str:
    """Sanitize module name for file system"""
    # Remove invalid characters and convert to lowercase
    return "".join(c for c in name.lower() if c.isalnum() or c in ['_', '-'])


def create_directory_if_not_exists(path: str):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def get_config_path() -> str:
    """Get the default config file path"""
    return os.path.join(os.getcwd(), "config.json")


def get_database_path() -> str:
    """Get the default database file path"""
    return os.path.join(os.getcwd(), "forelka.db")


def is_running_in_docker() -> bool:
    """Check if running in Docker container"""
    return os.path.exists('/.dockerenv')


def get_system_info() -> dict:
    """Get basic system information"""
    import platform
    import sys
    
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "user": getpass.getuser(),
        "is_docker": is_running_in_docker()
    }


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def safe_filename(filename: str) -> str:
    """Make filename safe for file system"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename