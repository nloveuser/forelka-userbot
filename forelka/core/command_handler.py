"""
Command handler for Forelka Userbot with improved architecture
"""

import re
import asyncio
from typing import Dict, List, Optional, Callable, Any, Tuple
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode


class CommandHandler:
    """Improved command handler with better architecture"""
    
    def __init__(self, bot):
        self.bot = bot
        self.commands: Dict[str, Dict[str, Any]] = {}
        self.aliases: Dict[str, str] = {}
    
    def register_command(self, name: str, func: Callable, module: str, 
                        description: str = "", usage: str = "", 
                        owner_only: bool = False, admin_only: bool = False):
        """Register a new command"""
        self.commands[name.lower()] = {
            "func": func,
            "module": module,
            "description": description,
            "usage": usage,
            "owner_only": owner_only,
            "admin_only": admin_only,
            "registered_at": asyncio.get_event_loop().time()
        }
    
    def register_alias(self, alias: str, command: str):
        """Register a command alias"""
        self.aliases[alias.lower()] = command.lower()
    
    def unregister_command(self, name: str):
        """Unregister a command"""
        if name.lower() in self.commands:
            del self.commands[name.lower()]
        
        # Remove any aliases pointing to this command
        aliases_to_remove = []
        for alias, cmd in self.aliases.items():
            if cmd == name.lower():
                aliases_to_remove.append(alias)
        
        for alias in aliases_to_remove:
            del self.aliases[alias]
    
    def create_message_handler(self):
        """Create a message handler for commands"""
        async def handle_message(client: Client, message: Message):
            """Handle incoming messages and process commands"""
            if not message.text:
                return
            
            # Get account-specific prefix
            prefix = getattr(client, 'prefix', '.')
            if not message.text.startswith(prefix):
                return
            
            # Parse command
            command_text = message.text[len(prefix):].strip()
            if not command_text:
                return
            
            parts = command_text.split(maxsplit=1)
            cmd_name = parts[0].lower()
            args = parts[1].split() if len(parts) > 1 else []
            
            # Check for aliases
            if cmd_name in self.aliases:
                cmd_name = self.aliases[cmd_name]
            
            # Check if command exists
            if cmd_name not in self.commands:
                return
            
            command = self.commands[cmd_name]
            
            # Check permissions
            if not await self._check_permissions(client, message, command):
                return
            
            # Execute command
            try:
                await command["func"](client, message, args)
            except Exception as e:
                await self._handle_command_error(client, message, cmd_name, e)
        
        return handle_message
    
    async def _check_permissions(self, client: Client, message: Message, command: Dict[str, Any]) -> bool:
        """Check if user has permission to execute command"""
        user_id = message.from_user.id if message.from_user else None
        account_id = getattr(client, 'account_id', None)
        
        # Check if command requires owner permissions
        if command.get("owner_only", False):
            if not await self.bot.db.is_owner(account_id, user_id):
                await message.reply(
                    "❌ <b>Access denied</b>\n"
                    "This command is only available to account owners.",
                    parse_mode=ParseMode.HTML
                )
                return False
        
        # Check if command requires admin permissions
        if command.get("admin_only", False):
            # For now, admins are also owners
            if not await self.bot.db.is_owner(account_id, user_id):
                await message.reply(
                    "❌ <b>Access denied</b>\n"
                    "This command is only available to admins.",
                    parse_mode=ParseMode.HTML
                )
                return False
        
        return True
    
    async def _handle_command_error(self, client: Client, message: Message, command_name: str, error: Exception):
        """Handle command execution errors"""
        import traceback
        
        error_msg = (
            f"❌ <b>Command Error</b>\n"
            f"<b>Command:</b> <code>{command_name}</code>\n"
            f"<b>Error:</b> <code>{str(error)}</code>\n"
            f"<b>Module:</b> <code>{self.commands.get(command_name, {}).get('module', 'Unknown')}</code>"
        )
        
        try:
            await message.reply(error_msg, parse_mode=ParseMode.HTML)
        except:
            pass  # Ignore if we can't send the error message
        
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Command {command_name} failed: {error}", exc_info=True)
    
    def get_command_list(self, account_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of available commands"""
        commands = []
        
        for name, cmd in self.commands.items():
            # Skip owner-only commands if no account_id provided
            if cmd.get("owner_only", False) and account_id is None:
                continue
            
            commands.append({
                "name": name,
                "description": cmd.get("description", ""),
                "usage": cmd.get("usage", ""),
                "module": cmd.get("module", ""),
                "owner_only": cmd.get("owner_only", False),
                "admin_only": cmd.get("admin_only", False)
            })
        
        return sorted(commands, key=lambda x: x["name"])
    
    def get_command_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific command"""
        cmd = self.commands.get(name.lower())
        if not cmd:
            return None
        
        return {
            "name": name.lower(),
            "description": cmd.get("description", ""),
            "usage": cmd.get("usage", ""),
            "module": cmd.get("module", ""),
            "owner_only": cmd.get("owner_only", False),
            "admin_only": cmd.get("admin_only", False),
            "registered_at": cmd.get("registered_at")
        }
    
    def search_commands(self, query: str) -> List[Dict[str, Any]]:
        """Search commands by name or description"""
        query = query.lower()
        results = []
        
        for name, cmd in self.commands.items():
            if (query in name.lower() or 
                query in cmd.get("description", "").lower() or
                query in cmd.get("module", "").lower()):
                
                results.append({
                    "name": name,
                    "description": cmd.get("description", ""),
                    "usage": cmd.get("usage", ""),
                    "module": cmd.get("module", ""),
                    "owner_only": cmd.get("owner_only", False)
                })
        
        return sorted(results, key=lambda x: x["name"])
    
    def get_aliases(self) -> Dict[str, str]:
        """Get all command aliases"""
        return dict(self.aliases)
    
    def clear_commands(self):
        """Clear all registered commands and aliases"""
        self.commands.clear()
        self.aliases.clear()