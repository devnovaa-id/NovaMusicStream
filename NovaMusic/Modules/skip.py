
from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.types import MediaStream

from NovaMusic import BOT_USERNAME, LOGGER, app, novadb, pytgcalls  # ✅ LOGGER ditambahkan
from NovaMusic.Helpers import _clear_, admin_check, buttons, close_key, gen_thumb
from NovaMusic.Helpers.active import add_active_chat, remove_active_chat


@app.on_message(filters.command(["skip", "next"]) & filters.group)
@admin_check
async def skip_str(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    get = novadb.get(message.chat.id)
    if not get:
        try:
            await _clear_(message.chat.id)
            await remove_active_chat(message.chat.id)
            await pytgcalls.leave_call(message.chat.id)
            await message.reply_text(
                text=f"➻ sᴛʀᴇᴀᴍ sᴋɪᴩᴩᴇᴅ 🥺\n│ \n└ʙʏ : {message.from_user.mention} 🥀\n\n**» ɴᴏ ᴍᴏʀᴇ ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs ɪɴ** {message.chat.title}, **ʟᴇᴀᴠɪɴɢ ᴠɪᴅᴇᴏᴄʜᴀᴛ.**",
                reply_markup=close_key,
            )
        except:
            return
    else:
        title = get[0]["title"]
        duration = get[0]["duration"]
        file_path = get[0]["file_path"]
        videoid = get[0]["videoid"]
        req_by = get[0]["req"]
        user_id = get[0]["user_id"]
        get.pop(0)

        stream = MediaStream(file_path)
        try:
            await pytgcalls.play(message.chat.id, stream)
            await add_active_chat(message.chat.id)
        except Exception as e:
            LOGGER.error(f"Skip play error: {e}")
            await _clear_(message.chat.id)
            await remove_active_chat(message.chat.id)
            return await pytgcalls.leave_call(message.chat.id)

        await message.reply_text(
            text=f"➻ sᴛʀᴇᴀᴍ sᴋɪᴩᴩᴇᴅ 🥺\n│ \n└ʙʏ : {message.from_user.mention} 🥀",
            reply_markup=close_key,
        )
        img = await gen_thumb(videoid, user_id)
        return await message.reply_photo(
            photo=img,
            caption=f"**➻ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ**\n\n‣ **ᴛɪᴛʟᴇ :** [{title[:27]}](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n‣ **ᴅᴜʀᴀᴛɪᴏɴ :** `{duration}` ᴍɪɴᴜᴛᴇs\n‣ **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {req_by}",
            reply_markup=buttons,
        )
