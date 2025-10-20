import os
import sys
from dotenv import load_dotenv
import discord
from discord.ext import commands
from pathlib import Path
import importlib.util
import requests
import json

# Load environment variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
if TOKEN is None or CLIENT_ID is None:
    raise ValueError("TOKEN and CLIENT_ID environment variables must be set")

# Initialize bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
commands_dir = Path("commands")

def load_command(scope):
    """Load a command module by name from the commands directory."""
    for file in commands_dir.glob("*.py"):
        command_name = file.stem  
        if command_name == scope:
            try:
                spec = importlib.util.spec_from_file_location(command_name, file)
                if spec is None or spec.loader is None:
                    print(f"Could not load spec or loader for {file}")
                    return None
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'name'):
                    print(f"Command loaded: {module.name}")
                    return module
                else:
                    print(f"Error loading command: {file}")
                    return None
            except Exception as e:
                print(f"Error loading command {file}: {e}")
                return None
    
    print(f"Command not found: {scope}")
    return None

def register_command(command):
    """Register the command globally in the Discord API."""
    if not command:
        print("There's no command to register.")
        return

    url = f"https://discord.com/api/v10/applications/{CLIENT_ID}/commands"  
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "name": command.name,
        "description": command.description,
        "options": getattr(command, 'options', []),
        "type": 1  
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body))
        print(f"Discord API response: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Failed to register command: {e}")

@bot.event
async def on_ready():
    print(f"Bot connected as: {bot.user}")
    
    if len(sys.argv) != 2:
        print("Usage: python register_commands.py <command_name>")
        await bot.close()
        return
    
    scope = sys.argv[1]
    command = load_command(scope)
    register_command(command)
    await bot.close()
   
    
bot.run(TOKEN)