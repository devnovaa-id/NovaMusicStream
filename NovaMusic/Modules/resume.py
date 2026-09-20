from pyrogram import filters
from pyrogram.types import Message

from NovaMusic import app, pytgcalls
from NovaMusic.Helpers import admin_check, close_key, get_mention, is_streaming, stream_on


@app.on_message(filters.command(["resume"]) & (filters.group | filters.channel))
@admin_check
async def res_str(_, message: Message):
    try:
        await message.delete()
    except:
        pass

    if await is_streaming(message.chat.id):
        return await message.reply_text("ᴅɪᴅ ʏᴏᴜ ʀᴇᴍᴇᴍʙᴇʀ ᴛʜᴀᴛ ʏᴏᴜ ᴘᴀᴜsᴇᴅ ᴛʜᴇ sᴛʀᴇᴀᴍ ?")
    await stream_on(message.chat.id)
    await pytgcalls.resume(message.chat.id)
    return await message.reply_text(
        text=f"➻ sᴛʀᴇᴀᴍ ʀᴇsᴜᴍᴇᴅ 💫\n│ \n└ʙʏ : {get_mention(message)} 🥀",
        reply_markup=close_key,
    )