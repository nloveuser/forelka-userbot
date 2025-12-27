"""
Configuration management for Forelka Userbot
"""

import json
import os
from typing import Any, Dict, Optional


class ConfigManager:
    """Configuration manager with JSON-based settings"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "database_path": "forelka.db",
            "log_level": "INFO",
            "web_interface": {
                "enabled": True,
                "host": "127.0.0.1",
                "port": 8080,
                "secret_key": "forelka-secret-key-change-me"
            },
            "inline_bot": {
                "enabled": True,
                "token": "",
                "owner_id": 0
            },
            "modules": {
                "auto_load": True,
                "modules_dir": "modules",
                "loaded_modules_dir": "loaded_modules"
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️  Warning: Failed to load config file: {e}")
                print("Using default configuration...")
        
        # Save the merged config
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config(self.config)
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        for key, value in updates.items():
            self.set(key, value)
    
    def get_web_config(self) -> Dict[str, Any]:
        """Get web interface configuration"""
        return self.get("web_interface", {})
    
    def get_inline_bot_config(self) -> Dict[str, Any]:
        """Get inline bot configuration"""
        return self.get("inline_bot", {})
    
    def get_modules_config(self) -> Dict[str, Any]:
        """Get modules configuration"""
        return self.get("modules", {})
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = {
            "database_path": "forelka.db",
            "log_level": "INFO",
            "web_interface": {
                "enabled": True,
                "host": "127.0.0.1",
                "port": 8080,
                "secret_key": "forelka-secret-key-change-me"
            },
            "inline_bot": {
                "enabled": True,
                "token": "",
                "owner_id": 0
            },
            "modules": {
                "auto_load": True,
                "modules_dir": "modules",
                "loaded_modules_dir": "loaded_modules"
            }
        }
        self._save_config(self.config)
    
    def create_sample_config(self, path: str = "config.sample.json"):
        """Create a sample configuration file"""
        sample_config = {
            "database_path": "forelka.db",
            "log_level": "INFO",
            "web_interface": {
                "enabled": True,
                "host": "127.0.0.1",
                "port": 8080,
                "secret_key": "your-secret-key-here"
            },
            "inline_bot": {
                "enabled": True,
                "token": "your-bot-token-here",
                "owner_id": 123456789
            },
            "modules": {
                "auto_load": True,
                "modules_dir": "modules",
                "loaded_modules_dir": "loaded_modules"
            }
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Sample configuration created at: {path}")