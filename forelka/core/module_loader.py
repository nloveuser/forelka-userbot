"""
Module loader for Forelka Userbot with improved architecture
"""

import os
import importlib.util
import sys
import subprocess
import asyncio
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path


class DependencyHandler:
    """Handle module dependencies"""
    
    @staticmethod
    def get_requirements(path: str) -> List[str]:
        """Extract requirements from module file"""
        if not path or not os.path.isfile(path):
            return []
        
        requirements = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# requirements:") or line.startswith("# scope: pip:"):
                        parts = line.split(":", 1)[1].strip().split()
                        requirements.extend(parts)
        except Exception as e:
            print(f"⚠️  Warning: Failed to read requirements from {path}: {e}")
        
        return requirements
    
    @classmethod
    def install_requirements(cls, path: str) -> bool:
        """Install module requirements"""
        requirements = cls.get_requirements(path)
        if not requirements:
            return True
        
        for req in requirements:
            try:
                importlib.import_module(req)
                print(f"✅ Dependency {req} already installed")
            except ImportError:
                try:
                    print(f"📦 Installing dependency: {req}")
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", req, "--quiet"
                    ])
                    print(f"✅ Installed {req}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to install {req}: {e}")
                    return False
        
        return True


class ModuleLoader:
    """Improved module loader with metadata support"""
    
    def __init__(self, bot):
        self.bot = bot
        self.loaded_modules: Dict[str, Dict[str, Any]] = {}
        self.module_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        modules_config = self.bot.config.get_modules_config()
        self.modules_dir = modules_config.get("modules_dir", "modules")
        self.loaded_modules_dir = modules_config.get("loaded_modules_dir", "loaded_modules")
        self.auto_load = modules_config.get("auto_load", True)
    
    async def load_all(self):
        """Load all modules from both directories"""
        print("📦 Loading modules...")
        
        # Create directories if they don't exist
        for directory in [self.modules_dir, self.loaded_modules_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
        
        # Load modules from both directories
        for directory in [self.modules_dir, self.loaded_modules_dir]:
            await self._load_directory(directory)
        
        print(f"✅ Loaded {len(self.loaded_modules)} modules")
    
    async def _load_directory(self, directory: str):
        """Load modules from a specific directory"""
        if not os.path.exists(directory):
            return
        
        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3].lower()
                module_path = os.path.join(directory, filename)
                
                if module_name in self.loaded_modules:
                    continue  # Already loaded
                
                await self.load_module(module_name, module_path)
    
    async def load_module(self, name: str, path: str) -> bool:
        """Load a single module"""
        try:
            # Install dependencies first
            if not DependencyHandler.install_requirements(path):
                print(f"❌ Failed to install dependencies for {name}")
                return False
            
            # Load the module
            spec = importlib.util.spec_from_file_location(f"module_{name}", path)
            if not spec or not spec.loader:
                print(f"❌ Failed to create module spec for {name}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Register the module
            if hasattr(module, "register"):
                try:
                    module.register(self.bot, self.bot.commands, name)
                    self.loaded_modules[name] = {
                        "path": path,
                        "module": module,
                        "loaded_at": asyncio.get_event_loop().time()
                    }
                    self._extract_metadata(name, module)
                    
                    # Register in database
                    account_id = 1  # Default account for now
                    await self.bot.db.register_module(
                        account_id, name,
                        self.module_metadata[name].get("version", "1.0"),
                        self.module_metadata[name].get("developer", "Unknown"),
                        self.module_metadata[name].get("description", "")
                    )
                    
                    print(f"✅ Loaded module: {name}")
                    return True
                    
                except Exception as e:
                    print(f"❌ Failed to register module {name}: {e}")
                    return False
            else:
                print(f"⚠️  Module {name} has no register function")
                return False
                
        except Exception as e:
            print(f"❌ Failed to load module {name}: {e}")
            return False
    
    def _extract_metadata(self, name: str, module) -> Dict[str, Any]:
        """Extract metadata from module"""
        metadata = {
            "name": name,
            "developer": getattr(module, "__developer__", "Unknown"),
            "version": getattr(module, "__version__", "1.0"),
            "description": getattr(module, "__description__", "No description"),
            "commands": getattr(module, "__commands__", []),
            "requirements": DependencyHandler.get_requirements(module.__file__ if hasattr(module, '__file__') else "")
        }
        
        self.module_metadata[name] = metadata
        return metadata
    
    async def unload_module(self, name: str) -> bool:
        """Unload a module"""
        if name not in self.loaded_modules:
            return False
        
        try:
            module = self.loaded_modules[name]["module"]
            if hasattr(module, "unregister"):
                module.unregister(self.bot, self.bot.commands, name)
            
            # Remove from loaded modules
            del self.loaded_modules[name]
            if name in self.module_metadata:
                del self.module_metadata[name]
            
            print(f"✅ Unloaded module: {name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to unload module {name}: {e}")
            return False
    
    async def unload_all(self):
        """Unload all modules"""
        print("🔄 Unloading modules...")
        
        for name in list(self.loaded_modules.keys()):
            await self.unload_module(name)
        
        print("✅ All modules unloaded")
    
    def get_module_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get module information"""
        return self.module_metadata.get(name)
    
    def get_all_modules(self) -> List[Dict[str, Any]]:
        """Get information about all loaded modules"""
        return list(self.module_metadata.values())
    
    def is_module_loaded(self, name: str) -> bool:
        """Check if module is loaded"""
        return name in self.loaded_modules
    
    def get_loaded_module_names(self) -> List[str]:
        """Get list of loaded module names"""
        return list(self.loaded_modules.keys())