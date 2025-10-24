import asyncio
import logging
import os
import tempfile
import discord
from discord import app_commands
import yt_dlp
from cloudinary import uploader

name = "download-from-youtube"
description = "Download a video, music or subtitle from a YouTube link."

MAX_FILE_SIZE = 100 * 1024 * 1024

@app_commands.choices(format=[
    app_commands.Choice(name="MP4", value="mp4"),
    app_commands.Choice(name="MP3", value="mp3"),
    # app_commands.Choice(name="SUB", value="sub"),
],
quality=[
    app_commands.Choice(name="LOW", value="low"),
    app_commands.Choice(name="MEDIUM", value="medium"),
    app_commands.Choice(name="HIGH", value="high")
]
)
async def execute(
    interaction: discord.Interaction,
    url: str,
    format: str,
    quality: str,
    private_response: bool = True,
):
    await interaction.response.defer(thinking=True, ephemeral=private_response)

    quality_map = {
        "low": "worst",
        "medium": "best[height<=480]",
        "high": "bestvideo+bestaudio/best",
    }
    ydl_quality = quality_map.get(quality, "best")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, f"%(title)s.%(ext)s")

        if format == "mp3":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": output_path,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
            }
        elif format == "mp4":
            ydl_opts = {
                "format": ydl_quality,
                "outtmpl": output_path,
                "merge_output_format": "mp4",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
            }
        # elif format == "sub":
        #     ydl_opts = {
        #         "skip_download": True,
        #         "writesubtitles": True,
        #         "writeautomaticsub": True, 
        #         "subtitleslangs": [subtitle_lang],
        #         "convert_subtitles": "srt",
        #         "outtmpl": output_path,
        #         "quiet": True,
        #         "no_warnings": True,
        #         "noplaylist": True,
        #     }
        else:
            await interaction.followup.send("Invalid format!", ephemeral=True)
            return

        loop = asyncio.get_running_loop()

        def download_youtube():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if format == "mp3":
                    filename = os.path.splitext(filename)[0] + ".mp3"
                return info, filename

        try:
            info, filename = await loop.run_in_executor(None, download_youtube)
            
            # if format == "sub":
            #     base_name = os.path.splitext(filename)[0]
            #     subtitle_path = None

            #     for f in os.listdir(tmpdir):
            #         if f.startswith(os.path.basename(base_name)) and (f.endswith(".vtt") or f.endswith(".srt")):
            #             subtitle_path = os.path.join(tmpdir, f)
            #             break

            #     if not subtitle_path:
            #         ydl_opts["writeautomaticsub"] = True
            #         info, filename = await loop.run_in_executor(None, download_youtube)
            #         for f in os.listdir(tmpdir):
            #             if f.startswith(os.path.basename(base_name)) and (f.endswith(".vtt") or f.endswith(".srt")):
            #                 subtitle_path = os.path.join(tmpdir, f)
            #                 break

            #     if not subtitle_path:
            #         await interaction.followup.send(
            #             f"No subtitles found for `{subtitle_lang}`.", ephemeral=True
            #         )
            #         return

            #     filename = subtitle_path

            file_size = os.path.getsize(filename)
            if file_size > MAX_FILE_SIZE:
                await interaction.followup.send(
                    f"File too large: {(file_size / (1024 * 1024)):.2f} MB.\n"
                    f"Please choose a lower quality or shorter video (limit: 100 MB).",
                    ephemeral=True,
                )
                return
            
            rtp = "video" if format in ["mp4", "mov", "webm", "mp3"] else "raw"

           
            upload_result = uploader.upload(
                filename,
                resource_type=rtp,
                folder="youtube_downloads",
                use_filename=True,
                unique_filename=False,
                overwrite=True,
            )

            url_result = upload_result["secure_url"]

          
            color_map = {
                "mp4": discord.Color.blurple(),
                "mp3": discord.Color.orange(),
                "sub": discord.Color.gold(),
            }
            embed_color = color_map.get(format, discord.Color.green())

           
            embed = discord.Embed(
                title="🎬 YouTube Download Complete!",
                description=(
                    f"**Your file was successfully downloaded!**\n\n"
                    f"**Title:** `{info.get('title')}`\n"
                    f"**Format:** `{format.upper()}`\n"
                    f"**Quality:** `{quality}`\n\n"
                    f"[▶️ **View / Download Here**]({url_result})"
                ),
                color=embed_color,
            )
            embed.set_footer(text="yt-dlp • Cloud Upload • Powered by FFmpeg")
            if info.get("thumbnail"):
                embed.set_thumbnail(url=info.get("thumbnail"))
            if format == "mp4":
                embed.set_image(url=url_result)

            await interaction.followup.send(embed=embed, ephemeral=private_response)

        except Exception as e:
            logging.exception(f"YouTube download failed: {e}")
            await interaction.followup.send(
                "Internal error occurred.", ephemeral=private_response
            )