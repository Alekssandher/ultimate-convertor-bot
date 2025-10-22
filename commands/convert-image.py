
import logging
import os
import tempfile
import discord
from discord import app_commands
from cloudinary import uploader
from PIL import Image

MAX_FILE_SIZE = 45 * 1024 * 1024
NO_ALPHA_FORMATS = (
    "JPEG", "JPG", "BMP", "ICO", "MPO" 
)

name="convert-image"
description = "Convert an image file to another vidimageeo type"

def convert_img(tmp_input_path: str, tmp_output_path: str, format:str ):
    image = Image.open(tmp_input_path)
    
    if format in NO_ALPHA_FORMATS and image.mode in ("RGBA", "LA", "P"):
        image = image.convert("RGB")

    image.save(tmp_output_path, format)

@app_commands.describe(file="The image file to convert", format="Target image format", link_in_chat="See the image result in chat", private_response="Private response")
@app_commands.choices(format=[
    app_commands.Choice(name="JPEG", value="JPEG"),
    app_commands.Choice(name="JPG", value="JPG"),
    app_commands.Choice(name="PNG", value="PNG"),
    app_commands.Choice(name="WEBP", value="WEBP"),
    app_commands.Choice(name="GIF", value="GIF"),
    app_commands.Choice(name="BMP", value="BMP"),
    app_commands.Choice(name="TIFF", value="TIFF"),
    app_commands.Choice(name="ICO", value="ICO"),
    app_commands.Choice(name="JP2", value="JP2"),
    app_commands.Choice(name="AVIF", value="AVIF")
])
async def execute(interaction: discord.Interaction, file: discord.Attachment, format: str, link_in_chat: bool = False, private_response: bool = True):

    await interaction.response.defer(thinking=True)
    
    if file.size > MAX_FILE_SIZE:
        await interaction.followup.send(f"File too big ({file.size / (1024*1024):.2f} MB).", ephemeral=private_response)
        return
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.rsplit('.',1)[1]}") as tmp_input:
        tmp_input.write(await file.read())
        tmp_input_path = tmp_input.name

    tmp_output_path = tmp_input_path.rsplit('.', 1)[0] + f".{format}"

    try:
        
        convert_img(tmp_input_path, tmp_output_path, format)
        
        upload_result = uploader.upload(
                tmp_output_path,
                resource_type="image",
                folder="image_conversions",
                use_filename=True,
                unique_filename=False,
                overwrite=True
            )
        
        url = upload_result["secure_url"]

        embed = discord.Embed(
            title="🎬 Image Conversion Complete!",
            description=(
                f"✅ **Your image was successfully converted!**\n\n"
                f"**Original:** `{file.filename}`\n"
                f"**Format:** `{format.upper()}`\n"
                f"[▶️ **Download Here**]({url})"
            ),
            color=discord.Color.green()
        )

        embed.set_footer(text="Pillow Conversion • Powered by Cloudinary")
        embed.set_thumbnail(url=url)

        await interaction.followup.send(embed=embed, ephemeral=private_response)
        if link_in_chat:
            await interaction.followup.send(
                f"**{interaction.user.mention}, here’s your converted image:**\n{url}", ephemeral=private_response
            )

    except Exception as e:
        logging.error(f"Error converting image: {e}")
    finally:
        for path in (tmp_input_path, tmp_output_path):
                if os.path.exists(path):
                    os.remove(path)