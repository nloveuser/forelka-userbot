from typing import Callable, Optional, List, Dict, Any
from functools import wraps
from pyrogram.types import Message


def command(name: str, description: str = "", usage: str = "", 
           owner_only: bool = False, admin_only: bool = False):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(client, message: Message, args: List[str]):
            try:
                return await func(client, message, args)
            except Exception as e:
                await client.bot.utils.handle_command_error(client, message, name, e)
        
        wrapper._command_info = {
            'name': name,
            'description': description,
            'usage': usage,
            'owner_only': owner_only,
            'admin_only': admin_only
        }
        return wrapper
    return decorator


def owner_only(func: Callable):
    @wraps(func)
    async def wrapper(client, message: Message, args: List[str]):
        account_id = getattr(client, 'account_id', 1)
        user_id = message.from_user.id if message.from_user else None
        
        if not await client.bot.db.is_owner(account_id, user_id):
            await client.bot.utils.send_owner_only_message(client, message)
            return
        
        return await func(client, message, args)
    return wrapper


def admin_only(func: Callable):
    @wraps(func)
    async def wrapper(client, message: Message, args: List[str]):
        account_id = getattr(client, 'account_id', 1)
        user_id = message.from_user.id if message.from_user else None
        
        if not await client.bot.db.is_owner(account_id, user_id):
            await client.bot.utils.send_admin_only_message(client, message)
            return
        
        return await func(client, message, args)
    return wrapper


def public(func: Callable):
    @wraps(func)
    async def wrapper(client, message: Message, args: List[str]):
        return await func(client, message, args)
    return wrapper


def with_strings(func: Callable):
    @wraps(func)
    async def wrapper(client, message: Message, args: List[str]):
        if not hasattr(client.bot, 'strings'):
            from .strings import StringManager
            client.bot.strings = StringManager()
        
        return await func(client, message, args)
    return wrapper


def with_db(func: Callable):
    @wraps(func)
    async def wrapper(client, message: Message, args: List[str]):
        if not hasattr(client.bot, 'db'):
            from ..core.database import DatabaseManager
            client.bot.db = DatabaseManager()
        
        return await func(client, message, args)
    return wrapper