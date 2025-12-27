"""
Alias management module for Forelka Userbot
"""

__developer__ = "Kirillusha"
__version__ = "1.0"
__description__ = "Manage command aliases"


async def alias_cmd(client, message, args):
    """Manage command aliases"""
    account_id = getattr(client, 'account_id', 1)
    
    if not args:
        # Show all aliases
        aliases = await client.bot.db.get_all_settings(account_id)
        alias_settings = {k: v for k, v in aliases.items() if k.startswith('alias_')}
        
        if not alias_settings:
            await message.edit(
                "❌ <b>No aliases configured</b>",
                parse_mode="HTML"
            )
            return
        
        alias_list = "\n".join([f"• <code>{k[6:]}</code> → <code>{v}</code>" for k, v in alias_settings.items()])
        await message.edit(
            f"➡️ <b>Active Aliases</b>\n\n{alias_list}",
            parse_mode="HTML"
        )
        return
    
    if len(args) == 1:
        # Delete alias
        alias_name = args[0].lower()
        alias_key = f"alias_{alias_name}"
        
        current_aliases = await client.bot.db.get_all_settings(account_id)
        if alias_key not in current_aliases:
            await message.edit(
                f"❌ <b>Alias</b> <code>{alias_name}</code> <b>not found</b>",
                parse_mode="HTML"
            )
            return
        
        await client.bot.db.set_setting(account_id, alias_key, None)
        await message.edit(
            f"✅ <b>Deleted alias:</b> <code>{alias_name}</code>",
            parse_mode="HTML"
        )
        return
    
    # Create alias
    alias_name = args[0].lower()
    target_command = args[1].lower()
    
    # Check if target command exists
    if target_command not in client.bot.commands.commands:
        await message.edit(
            f"❌ <b>Command</b> <code>{target_command}</code> <b>not found</b>",
            parse_mode="HTML"
        )
        return
    
    alias_key = f"alias_{alias_name}"
    await client.bot.db.set_setting(account_id, alias_key, target_command)
    
    # Update command handler aliases
    client.bot.commands.register_alias(alias_name, target_command)
    
    await message.edit(
        f"✅ <b>Created alias:</b> <code>{alias_name}</code> → <code>{target_command}</code>",
        parse_mode="HTML"
    )


def register(bot, commands, module_name):
    """Register the alias module"""
    commands.register_command("alias", alias_cmd, module_name,
                            description="Manage command aliases",
                            usage=".alias [name] [target]")