from pyrogram import Client
import os

print("=== PYROGRAM SESSION GENERATOR ===\n")
api_id = int(input("Masukkan API ID: "))
api_hash = input("Masukkan API HASH: ")

# Use a temporary file session (will be deleted after)
session_file = "temp_session"
app = Client(session_file, api_id=api_id, api_hash=api_hash)

async def main():
    async with app:
        print("\n📱 Sedang memproses...\n")
        # Export string session
        string_session = await app.export_session_string()
        print("\n✨ Berikut adalah String Session kamu:")
        print("=" * 50)
        print(string_session)
        print("=" * 50)
        print("\n⚠️ JANGAN BAGIKAN KODE INI KEPADA SIAPAPUN!")
    # Clean up temporary session file
    if os.path.exists(f"{session_file}.session"):
        os.remove(f"{session_file}.session")

import asyncio
asyncio.run(main())