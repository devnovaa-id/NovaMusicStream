from pyrogram import filters
from pyrogram.types import Message

from NovaMusic import app, pytgcalls
from NovaMusic.Helpers import admin_check, close_key, get_mention, is_streaming, stream_off


@app.on_message(filters.command(["pause"]) & (filters.group | filters.channel))
@admin_check
async def pause_str(_, message: Message):
    try:
        await message.delete()
    except:
        pass

    if not await is_streaming(message.chat.id):
        return await message.reply_text(
            "ᴅɪᴅ ʏᴏᴜ ʀᴇᴍᴇᴍʙᴇʀ ᴛʜᴀᴛ ʏᴏᴜ ʀᴇsᴜᴍᴇᴅ ᴛʜᴇ sᴛʀᴇᴀᴍ ?"
        )

    await pytgcalls.pause(message.chat.id)
    await stream_off(message.chat.id)
    return await message.reply_text(
        text=f"➻ sᴛʀᴇᴀᴍ ᴩᴀᴜsᴇᴅ 🥺\n│ \n└ʙʏ : {get_mention(message)} 🥀",
        reply_markup=close_key,
    )