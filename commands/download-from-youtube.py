import discord
from discord import app_commands

name = "download-from-youtube"
description = "Download a video, music or subtitle from a YouTube link."

@app_commands.choices(format=[
    app_commands.Choice(name="MP4", value="mp4"),
    app_commands.Choice(name="MP3", value="mp3"),
    app_commands.Choice(name="SUB", value="sub"),
],
quality=[
    app_commands.Choice(name="LOW", value="low"),
    app_commands.Choice(name="MEDIUM", value="medium"),
    app_commands.Choice(name="HIGH", value="high")
]
)
async def execute(interaction: discord.Interaction, url: str, operation: str, quality: str, private_response: bool = True):
    return