# events/on_ready.py
import logging
from discord import Object
from utils.command_loader import register_commands
from pathlib import Path



async def on_ready(bot, guild_id, DEV_ENV):
    """Handle the on_ready event and sync commands."""
    logger = logging.getLogger('discord')
    logger.info(f'{bot.user} has connected to Discord!')

    logger.info("Commands in tree before sync:")
    for cmd in bot.tree.get_commands():
        desc = getattr(cmd, "description", "<no description>")
        logger.info(f"- {cmd.name} ({desc})")

    commands_dir = Path("commands")

    await register_commands(bot, commands_dir)

    try:
        if DEV_ENV:
           
            synced = await bot.tree.sync(guild=Object(id=guild_id))
            logger.info(f"Synced {len(synced)} command(s) to guild {guild_id}")
        else:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} command(s) globally")
        for cmd in synced:
            logger.info(f"Synced command: {cmd.name}")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")