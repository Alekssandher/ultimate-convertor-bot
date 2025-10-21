import os
import cloudinary
from dotenv import load_dotenv
from discord import Intents

def load_config():
    """Load environment variables and bot configuration."""
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    GUILD_ID = os.getenv('GUILD_ID')  
    DEV_ENV = os.getenv('DEV_ENV', '').lower() in ('1', 'true', 'yes')
    CDN_NAME=os.getenv("CDN_NAME")
    CDN_KEY=os.getenv("CDN_KEY")
    CDN_SECRET=os.getenv("CDN_SECRET")

    if TOKEN is None:
        raise ValueError("TOKEN environment variable is not set")
    if CDN_NAME is None and CDN_KEY is None and CDN_SECRET is None:
        raise ValueError("Configure the Cloudinary Env Variables")
    
    intents = Intents.default()
    intents.message_content = True
    
    cloudinary.config(
        cloud_name=CDN_NAME,
        api_key=CDN_KEY,
        api_secret=CDN_SECRET
    )
    return {
        'TOKEN': TOKEN,
        'GUILD_ID': GUILD_ID,
        'DEV_ENV': DEV_ENV,
        # 'CDN_NAME': CDN_NAME,
        # 'CDN_KEY': CDN_KEY,
        # 'CDN_SECRET': CDN_SECRET,
        'intents': intents
    }