# main.py
import discord
from discord import app_commands
from discord.ext import commands
from config import load_config
from utils.logger import setup_logging
from events.on_ready import on_ready as handle_on_ready

config = load_config()
TOKEN = config['TOKEN']
GUILD_ID = config['GUILD_ID']
DEV_ENV = config['DEV_ENV']

intents = config['intents']

bot = commands.Bot(command_prefix="!", intents=intents)

logger = setup_logging()

@bot.event
async def on_ready():
    await handle_on_ready(bot, GUILD_ID, DEV_ENV)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle errors during slash command execution."""
    command_name = interaction.command.name if interaction.command else 'unknown'
    logger.error(f"Error in command {command_name}: {error}")
    if not interaction.response.is_done():
        try:
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
        except discord.InteractionResponded:
            await interaction.followup.send("An unexpected error occurred.", ephemeral=True)

bot.run(TOKEN)