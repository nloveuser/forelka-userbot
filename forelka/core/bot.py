import asyncio
import os
import sys
import signal
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from pyrogram import Client, idle
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from .database import DatabaseManager
from .config import ConfigManager
from .module_loader import ModuleLoader
from .command_handler import CommandHandler
from .logger import setup_logger
from ..utils.helpers import check_root_warning
from ..utils.strings import StringManager
from ..utils.messages import MessageManager

logger = logging.getLogger(__name__)


class ForelkaBot:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = ConfigManager(config_path)
        self.db = DatabaseManager(self.config.get("database_path", "forelka.db"))
        self.modules = ModuleLoader(self)
        self.commands = CommandHandler(self)
        self.strings = StringManager()
        self.messages = MessageManager(self)
        
        self.clients: Dict[int, Client] = {}
        self.running = False
        
        setup_logger(self.config.get("log_level", "INFO"))
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    async def start(self):
        logger.info("🚀 Starting Forelka Userbot...")
        
        check_root_warning()
        
        await self.db.initialize()
        await self.modules.load_all()
        
        accounts = await self.db.get_all_accounts()
        if not accounts:
            logger.warning("⚠️  No accounts configured. Please add accounts first.")
            return
        
        for account in accounts:
            await self._start_client(account)
        
        if not self.clients:
            logger.error("❌ No clients started successfully")
            return
        
        self.running = True
        logger.info(f"✅ Forelka started with {len(self.clients)} account(s)")
        
        await self._send_startup_notifications()
        await idle()
    
    async def _start_client(self, account: Dict[str, Any]):
        try:
            session_name = f"forelka-{account['user_id']}"
            client = Client(
                name=session_name,
                api_id=account['api_id'],
                api_hash=account['api_hash'],
                workdir=".",
                parse_mode=ParseMode.HTML
            )
            
            await client.start()
            
            client.account_id = account['id']
            client.user_id = account['user_id']
            client.prefix = account.get('prefix', '.')
            client.owners = await self.db.get_owners(account['id'])
            client.bot = self
            
            # Create log chat if not exists
            await self._create_log_chat(client)
            
            # Setup inline bot if enabled
            if self.config.get_inline_bot_config().get('enabled', True):
                await self._setup_inline_bot(client)
            
            client.add_handler(
                self.commands.create_message_handler(),
                group=0
            )
            
            self.clients[account['user_id']] = client
            logger.info(f"✅ Client started for user {account['user_id']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start client for user {account.get('user_id', 'unknown')}: {e}")
    
    async def _create_log_chat(self, client):
        """Create a dedicated log chat for the account"""
        try:
            # Create a private group for logs
            log_chat = await client.create_group_chat(
                title=f"Forelka Logs - {client.user_id}",
                users=["me"]
            )
            
            # Save log chat ID to database
            await self.db.set_setting(client.account_id, "log_chat_id", log_chat.id)
            
            # Send welcome message
            await client.send_message(
                log_chat.id,
                f"📝 <b>Forelka Log Chat</b>\n"
                f"Account: <code>{client.user_id}</code>\n"
                f"Log chat created successfully!"
            )
            
            logger.info(f"✅ Log chat created for user {client.user_id}: {log_chat.id}")
            
        except Exception as e:
            logger.warning(f"Failed to create log chat for user {client.user_id}: {e}")
    
    async def _setup_inline_bot(self, client):
        """Setup inline bot for the account"""
        try:
            inline_config = self.config.get_inline_bot_config()
            if not inline_config.get('token'):
                logger.warning("⚠️  Inline bot token not configured")
                return
            
            # Get Telegram ID from session
            me = await client.get_me()
            inline_config['owner_id'] = me.id
            
            # Save to database
            await self.db.set_setting(client.account_id, "inline_bot_token", inline_config['token'])
            await self.db.set_setting(client.account_id, "inline_bot_owner_id", me.id)
            
            logger.info(f"✅ Inline bot configured for user {client.user_id}")
            
        except Exception as e:
            logger.warning(f"Failed to setup inline bot for user {client.user_id}: {e}")
    
    async def _send_startup_notifications(self):
        for user_id, client in self.clients.items():
            try:
                await client.send_message(
                    "me",
                    f"🟢 <b>Forelka Userbot Started</b>\n"
                    f"👤 Account: <code>{user_id}</code>\n"
                    f"⚙️ Prefix: <code>{client.prefix}</code>\n"
                    f"📦 Modules: {len(self.modules.loaded_modules)} loaded\n"
                    f"🕒 Uptime: Just started"
                )
            except Exception as e:
                logger.warning(f"Failed to send startup notification to user {user_id}: {e}")
    
    async def stop(self):
        logger.info("🛑 Stopping Forelka Userbot...")
        
        self.running = False
        
        for user_id, client in self.clients.items():
            try:
                await client.stop()
                logger.info(f"✅ Client stopped for user {user_id}")
            except Exception as e:
                logger.error(f"❌ Failed to stop client for user {user_id}: {e}")
        
        self.clients.clear()
        await self.db.close()
        
        logger.info("👋 Forelka stopped")
    
    def _signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.stop())
    
    async def add_account(self, user_id: int, api_id: str, api_hash: str, prefix: str = "."):
        account_id = await self.db.add_account(user_id, api_id, api_hash, prefix)
        await self.db.add_owner(account_id, user_id)
        logger.info(f"✅ Added account {user_id} with ID {account_id}")
        return account_id
    
    async def remove_account(self, user_id: int):
        account = await self.db.get_account_by_user_id(user_id)
        if not account:
            return False
        
        if user_id in self.clients:
            await self.clients[user_id].stop()
            del self.clients[user_id]
        
        await self.db.remove_account(account['id'])
        logger.info(f"✅ Removed account {user_id}")
        return True
    
    async def get_account_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.get_account_by_user_id(user_id)
    
    async def get_all_accounts(self) -> List[Dict[str, Any]]:
        return await self.db.get_all_accounts()
    
    def get_client(self, user_id: int) -> Optional[Client]:
        return self.clients.get(user_id)
    
    async def reload_modules(self):
        logger.info("🔄 Reloading modules...")
        await self.modules.unload_all()
        await self.modules.load_all()
        logger.info("✅ Modules reloaded")
    
    async def broadcast_message(self, message: str):
        for user_id, client in self.clients.items():
            try:
                await client.send_message("me", message)
            except Exception as e:
                logger.warning(f"Failed to send broadcast to user {user_id}: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Forelka Userbot")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--root", action="store_true", help="Skip root user warnings")
    parser.add_argument("--add-account", nargs=3, metavar=("USER_ID", "API_ID", "API_HASH"), 
                       help="Add a new account")
    parser.add_argument("--remove-account", type=int, metavar="USER_ID",
                       help="Remove an account")
    parser.add_argument("--list-accounts", action="store_true",
                       help="List all configured accounts")
    
    args = parser.parse_args()
    
    if not args.root:
        check_root_warning()
    
    bot = ForelkaBot(args.config)
    
    if args.add_account:
        user_id, api_id, api_hash = args.add_account
        user_id = int(user_id)
        asyncio.run(bot.add_account(user_id, api_id, api_hash))
        print(f"✅ Added account {user_id}")
        return
    
    if args.remove_account:
        asyncio.run(bot.remove_account(args.remove_account))
        print(f"✅ Removed account {args.remove_account}")
        return
    
    if args.list_accounts:
        accounts = asyncio.run(bot.get_all_accounts())
        if not accounts:
            print("No accounts configured")
            return
        
        print("Configured accounts:")
        for account in accounts:
            print(f"- User ID: {account['user_id']}, Prefix: {account['prefix']}")
        return
    
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
        asyncio.run(bot.stop())


if __name__ == "__main__":
    main()