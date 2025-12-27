import time
from typing import List
from pyrogram.types import Message

from ..utils.decorators import command, with_strings, public


@command("ping", "Check bot response time", ".ping")
@with_strings
@public
async def ping_cmd(client, message: Message, args: List[str]):
    start_time = time.time()
    test_msg = await message.reply("<b>🏓 Pinging...</b>", parse_mode="HTML")
    end_time = time.time()
    response_time = (end_time - start_time) * 1000
    
    response_text = client.bot.strings.get('commands.ping.response_time')
    account_text = client.bot.strings.get('commands.ping.account')
    
    ping_text = (
        f"<b>{client.bot.strings.get('commands.ping.pong')}</b>\n"
        f"<b>{response_text.replace('{time}', str(round(response_time, 1)))}</b>\n"
        f"<b>{account_text.replace('{user_id}', str(client.user_id))}</b>"
    )
    
    await test_msg.edit(ping_text, parse_mode="HTML")


@command("uptime", "Show bot uptime", ".uptime")
@with_strings
@public
async def uptime_cmd(client, message: Message, args: List[str]):
    from ..utils.helpers import format_uptime
    
    start_time = getattr(client, '_start_time', time.time())
    uptime_seconds = time.time() - start_time
    
    uptime_text = (
        f"<b>⏰ Uptime</b>\n"
        f"<b>Duration:</b> <code>{format_uptime(uptime_seconds)}</code>\n"
        f"<b>Account:</b> <code>{client.user_id}</code>"
    )
    
    await client.bot.messages.send_message(client, message, uptime_text)


def register(bot, commands, module_name):
    commands.register_command("ping", ping_cmd, module_name,
                            description=ping_cmd._command_info['description'],
                            usage=ping_cmd._command_info['usage'])
    
    commands.register_command("uptime", uptime_cmd, module_name,
                            description=uptime_cmd._command_info['description'],
                            usage=uptime_cmd._command_info['usage'])