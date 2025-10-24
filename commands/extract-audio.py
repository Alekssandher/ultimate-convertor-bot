import os
import subprocess
import tempfile
import discord 
from cloudinary import uploader
import ffmpeg 

name = "extract-audio"
description = "Extract an audio from a video file"

MAX_FILE_SIZE = 25 * 1024 * 1024

def extract_audio(input_video, output_audio):
    command = [
        "ffmpeg",
        "-i", input_video,
        "-vn",
        "-acodec", "libmp3lame",
        "-q:a", "4",
        output_audio
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command, result.stderr)

async def execute(interaction: discord.Interaction, file: discord.Attachment, private_response: bool = True):

    await interaction.response.defer(thinking=True, ephemeral=private_response)

    if file.size > MAX_FILE_SIZE:
        await interaction.followup.send(f"File too big ({file.size / (1024*1024):.2f} MB).", ephemeral=private_response)
        return
    
    format = "mp3"

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.rsplit('.',1)[1]}") as tmp_input:
        tmp_input.write(await file.read())
        tmp_input_path = tmp_input.name
    
    tmp_output_path = tmp_input_path.rsplit('.', 1)[0] + f".{format}"

    try:
        extract_audio(tmp_input_path, tmp_output_path)

        upload_result = uploader.upload(
                tmp_output_path,
                resource_type="video",
                folder="audio_extractions",
                use_filename=True,
                unique_filename=False,
                overwrite=True
            )
        
        url = upload_result["secure_url"]

        embed = discord.Embed(
            title="🎬 Audio Extraction Complete!",
            description=(
                f"✅ **Your audio was successfully extracted!**\n\n"
                f"[▶️ **Download Here**]({url})"
            ),
            color=discord.Color.green()
        )

        embed.set_footer(text="Ffmpeg Conversion • Powered by Cloudinary")
        embed.set_thumbnail(url=url)

        await interaction.followup.send(embed=embed, ephemeral=private_response)
    except subprocess.CalledProcessError:
        await interaction.followup.send("There is no audio in this file.", ephemeral=private_response)
    finally:    
        for path in (tmp_input_path, tmp_output_path):
                if os.path.exists(path):
                    os.remove(path)