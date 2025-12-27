"""
Module loading module for Forelka Userbot
"""

__developer__ = "Kirillusha"
__version__ = "1.0"
__description__ = "Load and manage modules"


async def load_cmd(client, message, args):
    """Load a module"""
    if not args:
        await message.edit(
            "❌ <b>Usage:</b> <code>.load [module_name]</code>",
            parse_mode="HTML"
        )
        return
    
    module_name = args[0].lower()
    
    # Check if module is already loaded
    if client.bot.modules.is_module_loaded(module_name):
        await message.edit(
            f"❌ <b>Module</b> <code>{module_name}</code> <b>is already loaded</b>",
            parse_mode="HTML"
        )
        return
    
    # Try to load the module
    success = await client.bot.modules.load_module(module_name, f"modules/{module_name}.py")
    
    if success:
        await message.edit(
            f"✅ <b>Module loaded:</b> <code>{module_name}</code>",
            parse_mode="HTML"
        )
    else:
        await message.edit(
            f"❌ <b>Failed to load module:</b> <code>{module_name}</code>",
            parse_mode="HTML"
        )


async def unload_cmd(client, message, args):
    """Unload a module"""
    if not args:
        await message.edit(
            "❌ <b>Usage:</b> <code>.unload [module_name]</code>",
            parse_mode="HTML"
        )
        return
    
    module_name = args[0].lower()
    
    # Check if module is loaded
    if not client.bot.modules.is_module_loaded(module_name):
        await message.edit(
            f"❌ <b>Module</b> <code>{module_name}</code> <b>is not loaded</b>",
            parse_mode="HTML"
        )
        return
    
    # Unload the module
    success = await client.bot.modules.unload_module(module_name)
    
    if success:
        await message.edit(
            f"✅ <b>Module unloaded:</b> <code>{module_name}</code>",
            parse_mode="HTML"
        )
    else:
        await message.edit(
            f"❌ <b>Failed to unload module:</b> <code>{module_name}</code>",
            parse_mode="HTML"
        )


async def reload_cmd(client, message, args):
    """Reload all modules"""
    await message.edit(
        "🔄 <b>Reloading modules...</b>",
        parse_mode="HTML"
    )
    
    # Reload all modules
    await client.bot.reload_modules()
    
    await message.edit(
        "✅ <b>All modules reloaded</b>",
        parse_mode="HTML"
    )


async def modules_cmd(client, message, args):
    """Show loaded modules"""
    modules = client.bot.modules.get_all_modules()
    
    if not modules:
        await message.edit(
            "❌ <b>No modules loaded</b>",
            parse_mode="HTML"
        )
        return
    
    module_list = []
    for module in modules:
        name = module.get('name', 'Unknown')
        version = module.get('version', '1.0')
        developer = module.get('developer', 'Unknown')
        description = module.get('description', 'No description')
        
        module_list.append(f"• <code>{name}</code> (v{version}) by {developer} - {description}")
    
    modules_text = "\n".join(module_list)
    
    await message.edit(
        f"📦 <b>Loaded Modules ({len(modules)}):</b>\n\n{modules_text}",
        parse_mode="HTML"
    )


def register(bot, commands, module_name):
    """Register the load module"""
    commands.register_command("load", load_cmd, module_name,
                            description="Load a module",
                            usage=".load [module_name]")
    
    commands.register_command("unload", unload_cmd, module_name,
                            description="Unload a module",
                            usage=".unload [module_name]")
    
    commands.register_command("reload", reload_cmd, module_name,
                            description="Reload all modules",
                            usage=".reload")
    
    commands.register_command("modules", modules_cmd, module_name,
                            description="Show loaded modules",
                            usage=".modules")