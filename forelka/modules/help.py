import asyncio
from typing import List
from pyrogram.types import Message

from ..utils.decorators import command, with_strings, public


@command("help", "Show help information", ".help [command]")
@with_strings
@public
async def help_cmd(client, message: Message, args: List[str]):
    prefix = getattr(client, 'prefix', '.')
    
    if not args:
        help_text = (
            f"🤖 <b>{client.bot.strings.get('commands.help.title')}</b>\n\n"
            f"<b>{client.bot.strings.get('commands.help.basic')}</b>\n"
            f"<code>{prefix}help</code> - {client.bot.strings.get('commands.help.usage')}\n"
            f"<code>{prefix}ping</code> - {client.bot.strings.get('commands.ping.pong')}\n"
            f"<code>{prefix}prefix</code> - {client.bot.strings.get('commands.prefix.usage')}\n"
            f"<code>{prefix}owner</code> - {client.bot.strings.get('commands.owner.usage')}\n\n"
            f"<b>{client.bot.strings.get('commands.help.management')}</b>\n"
            f"<code>{prefix}modules</code> - {client.bot.strings.get('commands.modules.title')}\n"
            f"<code>{prefix}logs</code> - {client.bot.strings.get('commands.logs.title')}\n\n"
            f"<b>{client.bot.strings.get('commands.help.system')}</b>\n"
            f"<code>{prefix}update</code> - {client.bot.strings.get('commands.update.title')}\n\n"
            f"<b>{client.bot.strings.get('commands.help.usage')}</b>"
        )
        
        await client.bot.messages.send_message(client, message, help_text)
        return
    
    command_name = args[0].lower()
    command_info = client.bot.commands.get_command_info(command_name)
    
    if not command_info:
        await client.bot.messages.send_error(client, message, "commands.not_found", command=command_name)
        return
    
    help_text = (
        f"📖 <b>Command Help: {command_name}</b>\n\n"
        f"📝 <b>Description:</b> {command_info.get('description', 'No description available')}\n"
        f"🎯 <b>Usage:</b> <code>{command_info.get('usage', f'{prefix}{command_name}')}</code>\n"
        f"📦 <b>Module:</b> {command_info.get('module', 'Unknown')}\n\n"
        f"🔒 <b>Permissions:</b> {client.bot.strings.get_permission_text('owner_only' if command_info.get('owner_only', False) else 'public')}"
    )
    
    await client.bot.messages.send_message(client, message, help_text)


@command("search", "Search for commands", ".search [query]")
@with_strings
@public
async def search_cmd(client, message: Message, args: List[str]):
    if not args:
        await client.bot.messages.send_error(client, message, "commands.invalid_query")
        return
    
    query = ' '.join(args)
    results = client.bot.commands.search_commands(query)
    
    if not results:
        await client.bot.messages.send_error(client, message, "commands.search_no_results", query=query)
        return
    
    results = results[:10]
    prefix = getattr(client, 'prefix', '.')
    
    help_text = f"🔍 <b>Search Results for: {query}</b>\n\n"
    for cmd in results:
        usage = cmd.get('usage', f"{prefix}{cmd['name']}")
        desc = cmd.get('description', 'No description')
        help_text += f"• <code>{usage}</code> - {desc}\n"
    
    await client.bot.messages.send_message(client, message, help_text)


def register(bot, commands, module_name):
    commands.register_command("help", help_cmd, module_name,
                            description=help_cmd._command_info['description'],
                            usage=help_cmd._command_info['usage'])
    
    commands.register_command("search", search_cmd, module_name,
                            description=search_cmd._command_info['description'],
                            usage=search_cmd._command_info['usage'])