from typing import Optional
from pyrogram.types import Message
from pyrogram.enums import ParseMode


class MessageManager:
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'strings'):
            from .strings import StringManager
            bot.strings = StringManager()
    
    async def send_message(self, client, message: Message, text: str, 
                          parse_mode: ParseMode = ParseMode.HTML, 
                          reply_to: bool = True):
        """Send message with owner check"""
        user_id = message.from_user.id if message.from_user else None
        account_id = getattr(client, 'account_id', 1)
        
        is_owner = await self.bot.db.is_owner(account_id, user_id)
        
        if is_owner and reply_to:
            await message.edit(text, parse_mode=parse_mode)
        else:
            await message.reply(text, parse_mode=parse_mode)
    
    async def send_owner_only_message(self, client, message: Message):
        """Send owner-only access denied message"""
        text = self.bot.strings.get("errors.access_denied")
        await self.send_message(client, message, text)
    
    async def send_admin_only_message(self, client, message: Message):
        """Send admin-only access denied message"""
        text = self.bot.strings.get("errors.access_denied")
        await self.send_message(client, message, text)
    
    async def send_success(self, client, message: Message, text: str, **kwargs):
        """Send success message"""
        formatted_text = self.bot.strings.get(text, **kwargs)
        await self.send_message(client, message, f"✅ {formatted_text}")
    
    async def send_error(self, client, message: Message, text: str, **kwargs):
        """Send error message"""
        formatted_text = self.bot.strings.get(text, **kwargs)
        await self.send_message(client, message, f"❌ {formatted_text}")
    
    async def send_warning(self, client, message: Message, text: str, **kwargs):
        """Send warning message"""
        formatted_text = self.bot.strings.get(text, **kwargs)
        await self.send_message(client, message, f"⚠️ {formatted_text}")
    
    async def send_info(self, client, message: Message, text: str, **kwargs):
        """Send info message"""
        formatted_text = self.bot.strings.get(text, **kwargs)
        await self.send_message(client, message, f"ℹ️ {formatted_text}")
    
    async def handle_command_error(self, client, message: Message, command_name: str, error: Exception):
        """Handle command execution errors"""
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Command {command_name} failed: {error}", exc_info=True)
        
        error_text = self.bot.strings.get("errors.unknown_error", error=str(error))
        await self.send_error(client, message, error_text)