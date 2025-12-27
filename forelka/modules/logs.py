"""
Logs viewing module for Forelka Userbot
"""

__developer__ = "Kirillusha"
__version__ = "1.0"
__description__ = "View and manage bot logs"


async def logs_cmd(client, message, args):
    """View recent logs"""
    import os
    
    log_file = 'forelka.log'
    
    if not os.path.exists(log_file):
        await message.edit(
            "❌ <b>Log file not found</b>",
            parse_mode="HTML"
        )
        return
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            await message.edit(
                "📝 <b>Log file is empty</b>",
                parse_mode="HTML"
            )
            return
        
        # Show last 50 lines by default
        num_lines = 50
        if args and args[0].isdigit():
            num_lines = min(int(args[0]), 200)  # Limit to 200 lines max
        
        recent_logs = lines[-num_lines:]
        log_content = ''.join(recent_logs)
        
        # Truncate if too long
        if len(log_content) > 4000:
            log_content = log_content[-4000:]
            log_content = "...[truncated]...\n" + log_content
        
        await message.edit(
            f"<b>📄 Recent Logs (last {len(recent_logs)} lines):</b>\n\n"
            f"<code>{log_content}</code>",
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.edit(
            f"❌ <b>Error reading logs:</b> <code>{str(e)}</code>",
            parse_mode="HTML"
        )


async def clear_logs_cmd(client, message, args):
    """Clear log file"""
    import os
    
    log_file = 'forelka.log'
    
    if not os.path.exists(log_file):
        await message.edit(
            "📝 <b>Log file does not exist</b>",
            parse_mode="HTML"
        )
        return
    
    try:
        # Create backup before clearing
        backup_file = f"{log_file}.backup.{int(time.time())}"
        import shutil
        shutil.copy2(log_file, backup_file)
        
        # Clear the log file
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        await message.edit(
            f"✅ <b>Logs cleared</b>\n"
            f"<b>Backup created:</b> <code>{backup_file}</code>",
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.edit(
            f"❌ <b>Error clearing logs:</b> <code>{str(e)}</code>",
            parse_mode="HTML"
        )


def register(bot, commands, module_name):
    """Register the logs module"""
    commands.register_command("logs", logs_cmd, module_name,
                            description="View recent logs",
                            usage=".logs [num_lines]")
    
    commands.register_command("clearlogs", clear_logs_cmd, module_name,
                            description="Clear log file",
                            usage=".clearlogs")