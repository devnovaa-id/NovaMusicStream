import asyncio
from pyrogram import filters
from pyrogram.types import Message
from config import OWNER_ID
from NovaMusic import app, app2

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(_, message: Message):
    brep = await message.reply_text("sᴛᴀʀᴛᴇᴅ ᴀssɪsᴛᴀɴᴛ ʙʀᴏᴀᴅᴄᴀsᴛ...")
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text("**ᴇxᴀᴍᴘʟᴇ:**\n\n/broadcast [ᴍᴇssᴀɢᴇ] ᴏʀ [ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ]")
        query = message.text.split(None, 1)[1]
    sent = 0
    chats = []
    async for dialog in app2.iter_dialogs():
        chats.append(dialog.id)
    for i in chats:
        try:
            if message.reply_to_message:
                await app2.forward_messages(i, y, [x])
            else:
                await app2.send_message(i, query)
            sent += 1
        except Exception:
            continue
    try:
        await brep.edit_text(f"**ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ ᴍᴇssᴀɢᴇ ɪɴ {sent} ᴄʜᴀᴛs.**")
    except:
        await message.reply_text(f"**ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ ᴍᴇssᴀɢᴇ ɪɴ {sent} ᴄʜᴀᴛs.**")