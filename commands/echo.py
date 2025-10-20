from discord import app_commands, Interaction

name = "echo"
description = "Echoes a message."

@app_commands.describe(message="The message to echo.")
async def execute(interaction: Interaction, message: str) -> None:
    await interaction.response.send_message(message)