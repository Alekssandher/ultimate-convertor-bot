import requests
import os 
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
GUILD_ID = os.getenv("GUILD_ID")

if not TOKEN or not CLIENT_ID:
    print("Error: TOKEN or CLIENT_ID missing in .env")
    exit(1)

headers = {'Authorization': f'Bot {TOKEN}'}

global_url = f'https://discord.com/api/v10/applications/{CLIENT_ID}/commands'
global_response = requests.get(global_url, headers=headers)
print(f"Global Commands (Status {global_response.status_code}): {global_response.json()}")

if GUILD_ID:
    guild_url = f'https://discord.com/api/v10/applications/{CLIENT_ID}/guilds/{GUILD_ID}/commands'
    guild_response = requests.get(guild_url, headers=headers)
    print(f"Guild Commands for {GUILD_ID} (Status {guild_response.status_code}): {guild_response.json()}")
else:
    print("GUILD_ID not set, skipping guild command check")