"""
Prefix management module for Forelka Userbot
"""

__developer__ = "Kirillusha"
__version__ = "1.0"
__description__ = "Change command prefix for the account"


async def prefix_cmd(client, message, args):
    """Change command prefix"""
    account_id = getattr(client, 'account_id', 1)
    
    if not args:
        current_prefix = getattr(client, 'prefix', '.')
        await message.edit(
            f"⚙️ <b>Prefix Settings</b>\n"
            f"<b>Current prefix:</b> <code>{current_prefix}</code>\n"
            f"<b>Usage:</b> <code>.prefix [new_prefix]</code>",
            parse_mode="HTML"
        )
        return
    
    new_prefix = args[0][:3]  # Limit to 3 characters
    
    if not new_prefix or len(new_prefix) > 3:
        await message.edit(
            "❌ <b>Prefix must be 1-3 characters long</b>",
            parse_mode="HTML"
        )
        return
    
    # Update in database
    await client.bot.db.set_setting(account_id, "prefix", new_prefix)
    
    # Update client
    client.prefix = new_prefix
    
    await message.edit(
        f"✅ <b>Prefix changed to:</b> <code>{new_prefix}</code>",
        parse_mode="HTML"
    )


def register(bot, commands, module_name):
    """Register the prefix module"""
    commands.register_command("prefix", prefix_cmd, module_name,
                            description="Change command prefix",
                            usage=".prefix [new_prefix]")