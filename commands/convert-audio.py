import discord
from discord import app_commands

name = "convert-audio"
description = "Convert an audio file to another audio type"

#@bot.tree.command(name="convert-audio", description="Convert an audio file to another audio type")
@app_commands.describe(file="The audio file to convert", format="Target audio format")
@app_commands.choices(format=[
    app_commands.Choice(name="MP3", value="mp3"),
    app_commands.Choice(name="WAV", value="wav"),
    app_commands.Choice(name="OGG", value="ogg")
])
async def execute(interaction: discord.Interaction, file: discord.Attachment, format: str):
    await interaction.response.send_message(f"Converting {file.filename} to {format}...")
