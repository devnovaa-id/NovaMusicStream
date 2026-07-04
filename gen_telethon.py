import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

print("Meminta kode verifikasi...")
with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    client.start()
    print("\n✨ STRING SESSION (copy ini):")
    print(client.session.save())
