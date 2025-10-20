from discord import Interaction

name = "ping"
description = "Responds with Pong!"

async def execute(interaction: Interaction) -> None:
    await interaction.response.send_message("Pong!")