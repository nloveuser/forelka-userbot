import asyncio
import os
import shutil
import time
from typing import List
from pyrogram.types import Message

from ..utils.decorators import command, with_strings, owner_only


@command("backup", "Create a backup", ".backup")
@with_strings
@owner_only
async def backup_cmd(client, message: Message, args: List[str]):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    db_path = client.bot.db.db_path
    
    if os.path.exists(db_path):
        backup_db = f"{db_path}.backup.{timestamp}"
        shutil.copy2(db_path, backup_db)
        await client.bot.messages.send_success(client, message, "backup.created", file=backup_db)
    else:
        await client.bot.messages.send_error(client, message, "backup.file_not_found", file=db_path)


@command("restore", "Restore from backup", ".restore [backup_file]")
@with_strings
@owner_only
async def restore_cmd(client, message: Message, args: List[str]):
    if not args:
        await client.bot.messages.send_error(client, message, "commands.invalid_args")
        return
    
    backup_file = args[0]
    
    if not os.path.exists(backup_file):
        await client.bot.messages.send_error(client, message, "backup.file_not_found", file=backup_file)
        return
    
    try:
        await client.bot.messages.send_message(client, message, client.bot.strings.get("backup.applying"))
        
        db_path = client.bot.db.db_path
        shutil.copy2(backup_file, db_path)
        
        await client.bot.messages.send_success(client, message, "backup.restored", file=backup_file)
        
    except Exception as e:
        await client.bot.messages.send_error(client, message, "backup.restore_failed", error=str(e))


@command("listbackups", "List available backups", ".listbackups")
@with_strings
@owner_only
async def list_backups_cmd(client, message: Message, args: List[str]):
    import glob
    
    db_path = client.bot.db.db_path
    backup_pattern = f"{db_path}.backup.*"
    backups = glob.glob(backup_pattern)
    
    if not backups:
        await client.bot.messages.send_error(client, message, "backup.no_backups")
        return
    
    backups.sort(key=os.path.getmtime, reverse=True)
    
    backup_list = []
    for backup in backups[:10]:
        size = os.path.getsize(backup)
        mtime = os.path.getmtime(backup)
        from datetime import datetime
        date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        size_str = f"{size / 1024 / 1024:.1f}MB" if size > 1024*1024 else f"{size / 1024:.1f}KB"
        
        backup_list.append(f"• <code>{os.path.basename(backup)}</code> ({size_str}) - {date_str}")
    
    backup_text = f"{client.bot.strings.get('backup.available')}\n\n" + "\n".join(backup_list)
    await client.bot.messages.send_message(client, message, backup_text)


def register(bot, commands, module_name):
    commands.register_command("backup", backup_cmd, module_name,
                            description=backup_cmd._command_info['description'],
                            usage=backup_cmd._command_info['usage'])
    
    commands.register_command("restore", restore_cmd, module_name,
                            description=restore_cmd._command_info['description'],
                            usage=restore_cmd._command_info['usage'])
    
    commands.register_command("listbackups", list_backups_cmd, module_name,
                            description=list_backups_cmd._command_info['description'],
                            usage=list_backups_cmd._command_info['usage'])