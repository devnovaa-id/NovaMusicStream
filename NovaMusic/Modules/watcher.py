import logging
from pyrogram import filters as pyro_filters
from pyrogram.types import Message
from pytgcalls import filters
from pytgcalls.types import StreamEnded, MediaStream
from pytgcalls.exceptions import NoActiveGroupCall

from NovaMusic import BOT_ID, BOT_USERNAME, app, app2, novadb, pytgcalls
from NovaMusic.Helpers import _clear_, buttons, gen_thumb
from NovaMusic.Helpers.active import add_active_chat, remove_active_chat

logger = logging.getLogger("QueueWatcher")


@pytgcalls.on_update(filters.stream_end())
async def on_stream_end_handler(client, update: StreamEnded):
    chat_id = update.chat_id
    logger.info(f"Stream ended in chat {chat_id}")

    queue = novadb.get(chat_id)
    if not queue:
        logger.info(f"No more tracks in queue for {chat_id}, leaving call.")
        await _clear_(chat_id)
        await remove_active_chat(chat_id)
        await pytgcalls.leave_call(chat_id)
        try:
            await app.send_message(chat_id, "» **Antrian habis, saya tinggalkan voice chat.**")
        except Exception as e:
            logger.error(f"Failed to send queue empty message: {e}")
        return

    try:
        track = queue.pop(0)
        title = track["title"]
        duration = track["duration"]
        file_path = track["file_path"]
        videoid = track["videoid"]
        req_by = track["req"]
        user_id = track["user_id"]
        is_video = track.get("is_video", False)  # ambil flag
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing track from queue: {e}")
        await _clear_(chat_id)
        await remove_active_chat(chat_id)
        await pytgcalls.leave_call(chat_id)
        return

    stream = MediaStream(file_path)
    try:
        await pytgcalls.play(chat_id, stream)
        await add_active_chat(chat_id)
        logger.info(f"Now playing next track: {title}")
    except NoActiveGroupCall:
        logger.warning(f"No active group call in {chat_id} to play next track.")
        await _clear_(chat_id)
        await remove_active_chat(chat_id)
        return
    except Exception as e:
        logger.error(f"Failed to play next track: {e}")
        await _clear_(chat_id)
        await remove_active_chat(chat_id)
        await pytgcalls.leave_call(chat_id)
        return

    try:
        img = await gen_thumb(videoid, user_id)
        if img and img != "https://te.legra.ph/file/4c896584b592593c00aa8.jpg":
            await app.send_photo(
                chat_id=chat_id,
                photo=img,
                caption=f"**➻ ᴍᴇᴍᴜʟᴀɪ ᴘᴇᴍᴜᴛᴀʀᴀɴ**\n\n"
                        f"‣ **ᴊᴜᴅᴜʟ :** [{title[:27]}](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n"
                        f"‣ **ᴅᴜʀᴀsɪ :** `{duration}` ᴍᴇɴɪᴛ\n"
                        f"‣ **ᴅɪᴍɪɴᴛᴀ ᴏʟᴇʜ :** {req_by}",
                reply_markup=buttons,
            )
        else:
            await app.send_message(
                chat_id=chat_id,
                text=f"**➻ ᴍᴇᴍᴜʟᴀɪ ᴘᴇᴍᴜᴛᴀʀᴀɴ**\n\n"
                        f"‣ **ᴊᴜᴅᴜʟ :** [{title[:27]}](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n"
                        f"‣ **ᴅᴜʀᴀsɪ :** `{duration}` ᴍᴇɴɪᴛ\n"
                        f"‣ **ᴅɪᴍɪɴᴛᴀ ᴏʟᴇʜ :** {req_by}",
                reply_markup=buttons,
            )
    except Exception as e:
        logger.error(f"Error sending 'now playing' notification: {e}")


@app.on_message(pyro_filters.video_chat_ended)
async def video_chat_ended(_, message: Message):
    chat_id = message.chat.id
    logger.info(f"Video chat ended in {chat_id}")
    await _clear_(chat_id)
    await remove_active_chat(chat_id)
    await pytgcalls.leave_call(chat_id)


@app.on_message(pyro_filters.left_chat_member)
async def ub_leave(_, message: Message):
    if message.left_chat_member.id == BOT_ID:
        chat_id = message.chat.id
        logger.info(f"Bot removed from {chat_id}, cleaning up.")
        await _clear_(chat_id)
        await remove_active_chat(chat_id)
        await pytgcalls.leave_call(chat_id)
        try:
            await app2.leave_chat(chat_id)
        except Exception as e:
            logger.error(f"Assistant failed to leave chat {chat_id}: {e}")
