# delete_commands.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')

headers = {'Authorization': f'Bot {TOKEN}'}
url = f'https://discord.com/api/v10/applications/{CLIENT_ID}/commands'

response = requests.get(url, headers=headers)
commands = response.json()

for cmd in commands:
    delete_url = f'{url}/{cmd["id"]}'
    delete_response = requests.delete(delete_url, headers=headers)
    print(f"Deleted {cmd['name']}: {delete_response.status_code}")