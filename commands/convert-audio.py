import logging
import os
import tempfile
from cloudinary import uploader
import discord
from discord import app_commands

from pydub import AudioSegment

name = "convert-audio"
description = "Convert an audio file to another audio type"

ALLOWED_INPUT_TYPES = {
    "mp3", "wav", "ogg", "flac", "aac", "m4a", "wma", "opus", "amr", "aiff", "aif", "mp2"
}

MAX_FILE_SIZE = 10 * 1024 * 1024

#@bot.tree.command(name="convert-audio", description="Convert an audio file to another audio type")
@app_commands.describe(file="The audio file to convert", format="Target audio format", private_response="Private response")
@app_commands.choices(format=[
    app_commands.Choice(name="MP3", value="mp3"),
    app_commands.Choice(name="WAV", value="wav"),
    app_commands.Choice(name="FLAC", value="flac"),
    app_commands.Choice(name="OGG", value="ogg"),
    app_commands.Choice(name="AAC", value="aac"),
    app_commands.Choice(name="M4A", value="m4a"),
    app_commands.Choice(name="OPUS", value="opus"),
])
async def execute(interaction: discord.Interaction, file: discord.Attachment, format: str, private_response: bool = True):
    await interaction.response.defer(thinking=True, ephemeral=private_response)

    if file.size > MAX_FILE_SIZE:
        await interaction.followup.send(f"File too big ({file.size / (1024*1024):.2f} MB).", ephemeral=private_response)
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.rsplit('.',1)[1]}") as tmp_input:
        tmp_input.write(await file.read())
        tmp_input_path = tmp_input.name

    tmp_output_path = tmp_input_path.rsplit('.', 1)[0] + f".{format}"
    
    try:
        audio = AudioSegment.from_file(tmp_input_path)
        audio.export(tmp_output_path, format=format)

        # await interaction.followup.send(
        #     content=f"Conversion finished: `{os.path.basename(tmp_output_path)}`",
        #     file=discord.File(tmp_output_path),
        #     ephemeral=private_response
        # )

        upload_result = uploader.upload(
            tmp_output_path,
            resource_type="raw",
            folder="audio_conversions",
            use_filename=True,
            unique_filename=False,
            overwrite=True
        )
        url = upload_result["secure_url"]

        
        embed = discord.Embed(
            title="✅ Conversion Complete!",
            description=(
                f"Your file has been successfully converted!\n\n"
                f"**Original:** `{file.filename}`\n"
                f"**Converted to:** `{format.upper()}`\n"
                f"[⬇️ Click here to download]({url})"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="Audio Converter Bot • Powered by Cloudinary & FFmpeg")
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/727/727245.png") 

        await interaction.followup.send(embed=embed, ephemeral=private_response)

    except Exception as e:
        logging.error(f"Error converting image: {e}")
        embed_error = discord.Embed(
            title="Conversion Failed",
            description=f"An error occurred while converting your file.\n\n**Allowed formats:** {', '.join(ALLOWED_INPUT_TYPES)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed_error, ephemeral=private_response)

        
    finally:

        for path in (tmp_input_path, tmp_output_path):
            if os.path.exists(path):
                os.remove(path)