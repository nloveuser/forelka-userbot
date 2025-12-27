"""
Userbot information module for Forelka Userbot
"""

__developer__ = "Kirillusha"
__version__ = "1.0"
__description__ = "Show bot information and statistics"


async def ubinfo_cmd(client, message, args):
    """Show bot information"""
    import platform
    import sys
    import time
    from ..utils.helpers import format_uptime, get_system_info
    
    account_id = getattr(client, 'account_id', 1)
    user_id = getattr(client, 'user_id', 'Unknown')
    prefix = getattr(client, 'prefix', '.')
    
    # Get system information
    system_info = get_system_info()
    
    # Get account information
    account_info = await client.bot.db.get_account_by_id(account_id)
    
    # Get module information
    modules = client.bot.modules.get_all_modules()
    enabled_modules = [m for m in modules if m.get('enabled', True)]
    
    # Get owner information
    owners = await client.bot.db.get_owners(account_id)
    
    info_text = f"""
🤖 <b>Forelka Userbot Information</b>

📊 <b>Account Details:</b>
• <b>User ID:</b> <code>{user_id}</code>
• <b>Prefix:</b> <code>{prefix}</code>
• <b>Owners:</b> {len(owners)} user(s)
• <b>Account ID:</b> <code>{account_id}</code>

📦 <b>Modules:</b>
• <b>Total:</b> {len(modules)}
• <b>Enabled:</b> {len(enabled_modules)}
• <b>Disabled:</b> {len(modules) - len(enabled_modules)}

💻 <b>System Information:</b>
• <b>Platform:</b> {system_info.get('platform', 'Unknown')}
• <b>Python:</b> {system_info.get('python_version', 'Unknown').split()[0]}
• <b>User:</b> {system_info.get('user', 'Unknown')}
• <b>Docker:</b> {'Yes' if system_info.get('is_docker', False) else 'No'}

🔧 <b>Bot Details:</b>
• <b>Version:</b> {client.bot.__version__ if hasattr(client.bot, '__version__') else '2.0.0'}
• <b>Developer:</b> {client.bot.__author__ if hasattr(client.bot, '__author__') else 'Kirillusha'}
• <b>Working Directory:</b> {system_info.get('working_directory', 'Unknown')}
    """
    
    await message.edit(info_text.strip(), parse_mode="HTML")


async def stats_cmd(client, message, args):
    """Show bot statistics"""
    import time
    from ..utils.helpers import format_uptime
    
    account_id = getattr(client, 'account_id', 1)
    
    # Get basic stats
    start_time = getattr(client, '_start_time', time.time())
    uptime = time.time() - start_time
    
    # Get database stats
    accounts = await client.bot.db.get_all_accounts()
    owners_count = sum([len(await client.bot.db.get_owners(acc['id'])) for acc in accounts])
    
    # Get module stats
    modules = client.bot.modules.get_all_modules()
    enabled_modules = [m for m in modules if m.get('enabled', True)]
    
    stats_text = f"""
📈 <b>Forelka Statistics</b>

⏰ <b>Uptime:</b> <code>{format_uptime(uptime)}</code>

👥 <b>Accounts:</b> <code>{len(accounts)}</code>
👑 <b>Total Owners:</b> <code>{owners_count}</code>

📦 <b>Modules:</b>
• <b>Loaded:</b> <code>{len(modules)}</code>
• <b>Enabled:</b> <code>{len(enabled_modules)}</code>
• <b>Disabled:</b> <code>{len(modules) - len(enabled_modules)}</code>

💾 <b>Database:</b>
• <b>Path:</b> <code>{client.bot.db.db_path}</code>
• <b>Accounts:</b> <code>{len(accounts)}</code>
• <b>Owners:</b> <code>{owners_count}</code>
    """
    
    await message.edit(stats_text.strip(), parse_mode="HTML")


def register(bot, commands, module_name):
    """Register the ubinfo module"""
    commands.register_command("ubinfo", ubinfo_cmd, module_name,
                            description="Show bot information",
                            usage=".ubinfo")
    
    commands.register_command("stats", stats_cmd, module_name,
                            description="Show bot statistics",
                            usage=".stats")