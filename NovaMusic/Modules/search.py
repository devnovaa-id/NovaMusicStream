from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

from NovaMusic import app


@app.on_message(filters.command(["search"]))
async def ytsearch(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    try:
        if len(message.command) < 2:
            return await message.reply_text("» ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ sᴇᴀʀᴄʜ ʙᴀʙʏ !")
        query = " ".join(message.command[1:])
        m = await message.reply_text("🔎")

        results = await VideosSearch(query, limit=4).next()
        result_list = results.get("result", [])
        if not result_list:
            return await m.edit_text("» ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ ʜᴀsɪʟ ᴜɴᴛᴜᴋ ᴘᴇɴᴄᴀʀɪᴀɴ ɪɴɪ.")

        text = ""
        for i, res in enumerate(result_list[:4]):
            title = res.get("title", "Unknown")
            duration = res.get("duration", "0:00")
            view_count = res.get("viewCount", {})
            views = view_count.get("short", "N/A")
            channel = res.get("channel", {}).get("name", "Unknown")
            link = res.get("link")
            if not link:
                vid = res.get("id")
                link = f"https://youtube.com/watch?v={vid}" if vid else "#"
            text += f"✨ **ᴛɪᴛʟᴇ :** {title}\n"
            text += f"⏱ **ᴅᴜʀᴀᴛɪᴏɴ :** `{duration}`\n"
            text += f"👀 **ᴠɪᴇᴡs :** `{views}`\n"
            text += f"📣 **ᴄʜᴀɴɴᴇʟ :** {channel}\n"
            text += f"🔗 **ʟɪɴᴋ :** {link}\n\n"

        key = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data=f"forceclose abc|{message.from_user.id}")]]
        )
        await m.edit_text(
            text=text,
            reply_markup=key,
            disable_web_page_preview=True,
        )
    except Exception as e:
        await message.reply_text(f"Error: {e}")
