
import os
import requests
import yt_dlp
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

from NovaMusic import BOT_MENTION, BOT_USERNAME, LOGGER, app


@app.on_message(filters.command(["song", "vsong", "video", "music"]))
async def song(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    m = await message.reply_text("🔎")

    query = " ".join(str(i) for i in message.command[1:])
    if not query:
        return await m.edit_text("» ᴛᴏʟᴏɴɢ ᴍᴀsᴜᴋᴋᴀɴ ᴊᴜᴅᴜʟ ʟᴀɢᴜ.")

    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = await VideosSearch(query, limit=5).next()
        result_list = results.get("result", [])
        if not result_list:
            return await m.edit_text("» ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ ʜᴀsɪʟ ᴜɴᴛᴜᴋ ᴘᴇɴᴄᴀʀɪᴀɴ ɪɴɪ.")

        first_result = result_list[0]
        link = first_result.get("link")
        if not link:
            video_id = first_result.get("id")
            if video_id:
                link = f"https://youtube.com/watch?v={video_id}"
            else:
                return await m.edit_text("» ɢᴀɢᴀʟ ᴍᴇɴᴅᴀᴘᴀᴛᴋᴀɴ ʟɪɴᴋ ᴠɪᴅᴇᴏ.")
        else:
            # Ambil video_id dari link (jika ada)
            video_id = first_result.get("id")
            if not video_id:
                # Ekstrak dari link
                if "watch?v=" in link:
                    video_id = link.split("watch?v=")[-1].split("&")[0]
                else:
                    video_id = "unknown"

        title = first_result.get("title", "Unknown")[:40]
        thumbnail = first_result.get("thumbnails", [{}])[0].get("url", "")
        if thumbnail:
            thumbnail = thumbnail.split("?")[0]
        duration = first_result.get("duration", "0:00")

        # Download thumbnail
        thumb_name = f"thumb_{video_id or 'unknown'}.jpg"
        try:
            if thumbnail:
                thumb_data = requests.get(thumbnail, timeout=10, allow_redirects=True)
                if thumb_data.status_code == 200:
                    with open(thumb_name, "wb") as f:
                        f.write(thumb_data.content)
                else:
                    thumb_name = None
            else:
                thumb_name = None
        except Exception as e:
            LOGGER.warning(f"Thumb download error: {e}")
            thumb_name = None

    except Exception as ex:
        LOGGER.error(ex)
        return await m.edit_text(
            f"ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴛʀᴀᴄᴋ ғʀᴏᴍ ʏᴛ-ᴅʟ.\n\n**ʀᴇᴀsᴏɴ :** `{ex}`"
        )

    await m.edit_text("» ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ sᴏɴɢ,\n\nᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            if not info_dict:
                raise Exception("Gagal mengekstrak info audio.")
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)

        # ✅ Fallback untuk BOT_MENTION
        safe_bot = BOT_MENTION or "NovaMusic"
        rep = f"☁️ **ᴛɪᴛʟᴇ :** [{title[:23]}]({link})\n⏱️ **ᴅᴜʀᴀᴛɪᴏɴ :** `{duration}`\n🥀 **ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ :** {safe_bot}"

        # Hitung durasi dalam detik
        dur = 0
        try:
            parts = duration.split(":")
            secmul = 1
            for p in reversed(parts):
                dur += int(p) * secmul
                secmul *= 60
        except:
            dur = 0

        try:
            visit_butt = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="ʏᴏᴜᴛᴜʙᴇ", url=link)]]
            )
            await app.send_audio(
                chat_id=message.from_user.id,
                audio=audio_file,
                caption=rep,
                thumb=thumb_name if thumb_name and os.path.exists(thumb_name) else None,
                title=title,
                duration=dur,
                reply_markup=visit_butt,
            )
            if message.chat.type != ChatType.PRIVATE:
                await message.reply_text(
                    "ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴘᴍ, sᴇɴᴛ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ sᴏɴɢ ᴛʜᴇʀᴇ."
                )
        except Exception as e:
            LOGGER.error(f"Send audio error: {e}")
            start_butt = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="ᴄʟɪᴄᴋ ʜᴇʀᴇ", url=f"https://t.me/{BOT_USERNAME}?start")]]
            )
            return await m.edit_text(
                text="ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴀɴᴅ sᴛᴀʀᴛ ᴍᴇ ғᴏʀ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ sᴏɴɢs.",
                reply_markup=start_butt,
            )
        await m.delete()
    except Exception as e:
        LOGGER.error(e)
        return await m.edit_text(f"ғᴀɪʟᴇᴅ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴀᴜᴅɪᴏ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ sᴇʀᴠᴇʀs.\nError: {e}")

    finally:
        try:
            if os.path.exists(audio_file):
                os.remove(audio_file)
            if thumb_name and os.path.exists(thumb_name):
                os.remove(thumb_name)
        except Exception as ex:
            LOGGER.error(ex)
