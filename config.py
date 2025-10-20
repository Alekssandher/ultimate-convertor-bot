import os
from dotenv import load_dotenv
from discord import Intents

def load_config():
    """Load environment variables and bot configuration."""
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    GUILD_ID = os.getenv('GUILD_ID')  
    DEV_ENV = os.getenv('DEV_ENV', '').lower() in ('1', 'true', 'yes')

    if TOKEN is None:
        raise ValueError("TOKEN environment variable is not set")
    
    intents = Intents.default()
    intents.message_content = True
    
    return {
        'TOKEN': TOKEN,
        'GUILD_ID': GUILD_ID,
        'DEV_ENV': DEV_ENV,
        'intents': intents
    }