
import asyncio
import logging
import os
import tempfile
import discord
from discord import app_commands
from cloudinary import uploader
import ffmpeg

name = "convert-video"
description = "Convert an video file to another video type"

MAX_FILE_SIZE = 45 * 1024 * 1024
ALLOWED_VIDEO_TYPES = {"mp4", "webm", "avi", "mov", "mkv", "gif"}

def convert_video(input_path: str, output_path: str, output_format: str):
    (
        ffmpeg
        .input(input_path)
        .output(output_path, format=output_format)
        .run(overwrite_output=True)
    )

async def run_ffmpeg(input_path, output_path, target_format):
    loop = asyncio.get_running_loop()

    def ffmpeg_job():
        try:
            format_mapping = {
                'mp4': 'mp4',
                'mov': 'mov',
                'mkv': 'matroska',
                'webm': 'webm',
                'gif': 'gif',
            }
            ffmpeg_format = format_mapping.get(target_format.lower(), target_format)

            if ffmpeg_format == "gif":

                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_palette:
                    palette_path = temp_palette.name

                try:
                    stream = ffmpeg.input(input_path)
                    stream = stream.filter('fps', fps=15)
                    stream = stream.filter('scale', w=320, h=-1, flags='lanczos')
                    stream = stream.filter('palettegen')
                    stream.output(palette_path, vframes=1).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)

                    video_stream = ffmpeg.input(input_path)
                    palette_stream = ffmpeg.input(palette_path)
                    video_stream = video_stream.filter('fps', fps=15)
                    video_stream = video_stream.filter('scale', w=320, h=-1, flags='lanczos')
                    stream = ffmpeg.filter([video_stream, palette_stream], 'paletteuse', dither='bayer', bayer_scale=3)
                    stream.output(output_path, format='gif', loop=0).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
                finally:
                    if os.path.exists(palette_path):
                        os.remove(palette_path)
            else:
                stream = ffmpeg.input(input_path)
                stream.output(output_path, format=ffmpeg_format ).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            error_message = e.stderr.decode('utf-8') if e.stderr else str(e)
            raise Exception(f"FFmpeg error: {error_message}")
        except FileNotFoundError:
            raise Exception("FFmpeg binary not found. Ensure FFmpeg is installed and accessible.")
        except Exception as e:
            raise Exception(f"Error during FFmpeg processing: {str(e)}")

    await loop.run_in_executor(None, ffmpeg_job)

@app_commands.describe(file="The video file to convert", format="Target video format", private_response="Private response")
@app_commands.choices(format=[
    app_commands.Choice(name="MP4", value="mp4"),
    app_commands.Choice(name="MOV", value="mov"),
    app_commands.Choice(name="MKV", value="mkv"),
    app_commands.Choice(name="WEBM", value="webm"),
    app_commands.Choice(name="GIF", value="gif")
])
async def execute(interaction: discord.Interaction, file: discord.Attachment, format: str, private_response: bool = True):
    await interaction.response.defer(thinking=True, ephemeral=private_response)

    rtp = "video"
    if format == "gif":
        rtp = "raw"
        #MAX_FILE_SIZE = 9 * 1024 * 1024 

    if file.size > MAX_FILE_SIZE:
        await interaction.followup.send(f"File too big ({file.size / (1024*1024):.2f} MB).", ephemeral=private_response)
        return
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.rsplit('.',1)[1]}") as tmp_input:
        tmp_input.write(await file.read())
        tmp_input_path = tmp_input.name
    
    tmp_output_path = tmp_input_path.rsplit('.', 1)[0] + f".{format}"

    try:
        
        await run_ffmpeg(tmp_input_path, tmp_output_path, format)

        
        upload_result = uploader.upload(
                tmp_output_path,
                resource_type=rtp,
                folder="video_conversions",
                use_filename=True,
                unique_filename=False,
                overwrite=True
            )
        
        url = upload_result["secure_url"]

        await interaction.followup.send(f"url: {url}")
    except Exception as e:
        logging.error(f"Error converting video: {e}")
        embed_error = discord.Embed(
            title="Conversion Failed",
            description=f"An error occurred while converting your file.\n\n**Allowed formats:** {', '.join(ALLOWED_VIDEO_TYPES)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed_error, ephemeral=private_response)
         
    finally:    
        for path in (tmp_input_path, tmp_output_path):
                if os.path.exists(path):
                    os.remove(path)