import asyncio
import subprocess
import sys
from typing import List
from pyrogram.types import Message

from ..utils.decorators import command, with_strings, owner_only


@command("update", "Check for updates", ".update")
@with_strings
@owner_only
async def update_cmd(client, message: Message, args: List[str]):
    await client.bot.messages.send_message(client, message, client.bot.strings.get("update.checking"))
    
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            await client.bot.messages.send_error(client, message, "update.git_required")
            return
        
        subprocess.run(['git', 'fetch'], check=True, capture_output=True)
        result = subprocess.run(['git', 'status', '-uno'], capture_output=True, text=True)
        
        if 'Your branch is up to date' in result.stdout:
            await client.bot.messages.send_success(client, message, "update.latest")
        else:
            await client.bot.messages.send_warning(client, message, "update.available")
    
    except subprocess.CalledProcessError as e:
        await client.bot.messages.send_error(client, message, "update.failed", error=str(e))
    except Exception as e:
        await client.bot.messages.send_error(client, message, "update.failed", error=str(e))


@command("updateapply", "Apply updates", ".update apply")
@with_strings
@owner_only
async def update_apply_cmd(client, message: Message, args: List[str]):
    await client.bot.messages.send_message(client, message, client.bot.strings.get("update.applying"))
    
    try:
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True, check=True)
        
        await client.bot.messages.send_success(client, message, "update.applied")
        
        await client.bot.messages.send_message(client, message, client.bot.strings.get("update.restarting"))
        
        import os
        os.execv(sys.executable, ['python'] + sys.argv)
        
    except subprocess.CalledProcessError as e:
        await client.bot.messages.send_error(client, message, "update.failed", error=str(e))
    except Exception as e:
        await client.bot.messages.send_error(client, message, "update.failed", error=str(e))


def register(bot, commands, module_name):
    commands.register_command("update", update_cmd, module_name,
                            description=update_cmd._command_info['description'],
                            usage=update_cmd._command_info['usage'])
    
    commands.register_command("updateapply", update_apply_cmd, module_name,
                            description=update_apply_cmd._command_info['description'],
                            usage=update_apply_cmd._command_info['usage'])