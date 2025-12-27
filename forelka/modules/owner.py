"""
Owner management module for Forelka Userbot
"""

__developer__ = "Kirillusha"
__version__ = "1.0"
__description__ = "Manage account owners and permissions"


async def owner_cmd(client, message, args):
    """Manage account owners"""
    account_id = getattr(client, 'account_id', 1)
    user_id = message.from_user.id if message.from_user else None
    
    if not args and not message.reply_to_message:
        # Show current owners
        owners = await client.bot.db.get_owners(account_id)
        
        if not owners:
            await message.edit(
                "❌ <b>No owners configured for this account</b>",
                parse_mode="HTML"
            )
            return
        
        owner_list = "\n".join([f"• <code>{owner_id}</code>" for owner_id in owners])
        await message.edit(
            f"👑 <b>Account Owners</b>\n"
            f"<b>Account:</b> <code>{client.user_id}</code>\n\n"
            f"{owner_list}",
            parse_mode="HTML"
        )
        return
    
    # Handle adding/removing owners
    target_user_id = None
    
    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
    else:
        try:
            target_user_id = int(args[0])
        except (ValueError, IndexError):
            await message.edit(
                "❌ <b>Invalid user ID or reply required</b>",
                parse_mode="HTML"
            )
            return
    
    if target_user_id == client.user_id:
        await message.edit(
            "❌ <b>You cannot modify your own owner status</b>",
            parse_mode="HTML"
        )
        return
    
    # Check if user is already owner
    is_owner = await client.bot.db.is_owner(account_id, target_user_id)
    
    if is_owner:
        # Remove owner
        await client.bot.db.remove_owner(account_id, target_user_id)
        await message.edit(
            f"✅ <b>Removed owner:</b> <code>{target_user_id}</code>",
            parse_mode="HTML"
        )
    else:
        # Add owner
        await client.bot.db.add_owner(account_id, target_user_id, is_admin=False)
        await message.edit(
            f"✅ <b>Added owner:</b> <code>{target_user_id}</code>",
            parse_mode="HTML"
        )


async def admin_cmd(client, message, args):
    """Manage admin permissions (owner-only command)"""
    account_id = getattr(client, 'account_id', 1)
    user_id = message.from_user.id if message.from_user else None
    
    # Check if user is owner
    if not await client.bot.db.is_owner(account_id, user_id):
        await message.edit(
            "❌ <b>Access denied: Owner permissions required</b>",
            parse_mode="HTML"
        )
        return
    
    if not args and not message.reply_to_message:
        await message.edit(
            "❌ <b>Usage:</b> <code>.admin [user_id|reply]</code>",
            parse_mode="HTML"
        )
        return
    
    target_user_id = None
    
    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
    else:
        try:
            target_user_id = int(args[0])
        except (ValueError, IndexError):
            await message.edit(
                "❌ <b>Invalid user ID or reply required</b>",
                parse_mode="HTML"
            )
            return
    
    # For now, admins are also owners
    # In a future version, we could have separate admin permissions
    await client.bot.db.add_owner(account_id, target_user_id, is_admin=True)
    await message.edit(
        f"✅ <b>Granted admin permissions to:</b> <code>{target_user_id}</code>",
        parse_mode="HTML"
    )


def register(bot, commands, module_name):
    """Register the owner module"""
    commands.register_command("owner", owner_cmd, module_name,
                            description="Manage account owners",
                            usage=".owner [user_id|reply]",
                            owner_only=True)
    
    commands.register_command("admin", admin_cmd, module_name,
                            description="Grant admin permissions",
                            usage=".admin [user_id|reply]",
                            owner_only=True)