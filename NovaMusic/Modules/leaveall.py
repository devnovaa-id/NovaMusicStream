import asyncio
from pyrogram import filters
from pyrogram.types import Message
from config import OWNER_ID
from NovaMusic import ASS_MENTION, SUNAME, app, app2

@app.on_message(filters.command(["leaveall", "assleaveall"]) & filters.user(OWNER_ID))
async def ass_leaveall(_, message: Message):
    lear = await message.reply_text(f"» {ASS_MENTION} sᴛᴀʀᴛᴇᴅ ʟᴇᴀᴠɪɴɢ ᴄʜᴀᴛs...")
    left = 0
    failed = 0
    chats = []
    async for dialog in app2.iter_dialogs():
        chats.append(dialog.id)
    schat = (await app.get_chat(SUNAME)).id
    for i in chats:
        if i in (-1001686672798, int(schat)):
            continue
        try:
            await app2.leave_chat(i)
            left += 1
        except Exception:
            failed += 1
    try:
        await lear.edit_text(f"<u>**» {ASS_MENTION} sᴜᴄᴄᴇssғᴜʟʟʏ ʟᴇғᴛ ᴄʜᴀᴛs :**</u>\n\n**ʟᴇғᴛ :** `{left}`\n**ғᴀɪʟᴇᴅ :** `{failed}`")
    except:
        await message.reply_text(f"<u>**» {ASS_MENTION} sᴜᴄᴄᴇssғᴜʟʟʏ ʟᴇғᴛ ᴄʜᴀᴛs :**</u>\n\n**ʟᴇғᴛ :** `{left}`\n**ғᴀɪʟᴇᴅ :** `{failed}`")