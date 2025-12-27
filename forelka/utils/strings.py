import yaml
import os
from typing import Dict, Any, Optional


class StringManager:
    def __init__(self, language: str = "ru"):
        self.language = language
        self.strings = {}
        self.load_strings()
    
    def load_strings(self):
        strings_path = f"strings/{self.language}.yml"
        if os.path.exists(strings_path):
            with open(strings_path, 'r', encoding='utf-8') as f:
                self.strings = yaml.safe_load(f)
        else:
            # Fallback to Russian
            if self.language != "ru":
                self.language = "ru"
                self.load_strings()
    
    def get(self, key: str, **kwargs) -> str:
        keys = key.split('.')
        value = self.strings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return key
        
        if isinstance(value, str):
            try:
                return value.format(**kwargs)
            except KeyError:
                return value
        
        return str(value)
    
    def format(self, template: str, **kwargs) -> str:
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    
    def get_command_help(self, command_name: str) -> str:
        return self.get(f"commands.{command_name}.description", command=command_name)
    
    def get_permission_text(self, permission_type: str) -> str:
        return self.get(f"permissions.{permission_type}")
    
    def format_message(self, message_type: str, **kwargs) -> str:
        template = self.get(f"formatting.{message_type}")
        if template:
            return template.format(**kwargs)
        return str(kwargs.get('text', ''))