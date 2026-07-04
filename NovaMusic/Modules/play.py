import asyncio
import os
import logging
import yt_dlp

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import MediaStream
from telethon.errors import FloodWaitError, UserAlreadyParticipantError as TelethonUserAlreadyParticipantError
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest

from config import DURATION_LIMIT
from NovaMusic import (
    ASS_ID, ASS_MENTION, ASS_NAME, ASS_USERNAME,
    BOT_NAME, BOT_USERNAME, LOGGER, app, app2,
    novadb, pytgcalls,
)
from NovaMusic.Helpers.active import add_active_chat, is_active_chat, stream_on
from NovaMusic.Helpers.downloaders import (
    audio_dl,
    audio_dl_progress,
    search_youtube,
    get_playlist_videos,
    is_playlist_url,
)
from NovaMusic.Helpers.gets import get_file_name, get_url
from NovaMusic.Helpers.inline import buttons
from NovaMusic.Helpers.queue import put
from NovaMusic.Helpers.thumbnails import gen_qthumb, gen_thumb

logger = logging.getLogger("PlayModule")


@app.on_message(
    filters.command(["play", "vplay", "p"])
    & filters.group
    & ~filters.forwarded
    & ~filters.via_bot
)
async def play(_, message: Message):
    fallen = await message.reply_text("» ᴘʀᴏᴄᴇssɪɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...")
    try:
        await message.delete()
    except:
        pass

    try:
        get = await app.get_chat_member(message.chat.id, ASS_ID)
        if get.status == ChatMemberStatus.BANNED:
            unban_butt = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    text=f"ᴜɴʙᴀɴ {ASS_NAME}",
                    callback_data=f"unban_ass {message.chat.id}|{ASS_ID}",
                )
            ]])
            return await fallen.edit_text(
                f"» {ASS_NAME} ᴅɪʙᴀɴɴᴇᴅ ᴅɪ {message.chat.title}\n\n"
                f"𖢵 ɪᴅ : `{ASS_ID}`\n𖢵 ɴᴀᴍᴇ : {ASS_MENTION}\n"
                f"𖢵 ᴜsᴇʀɴᴀᴍᴇ : @{ASS_USERNAME}\n\nᴘʟᴇᴀsᴇ ᴜɴʙᴀɴ ᴀssɪsᴛᴀɴᴛ.",
                reply_markup=unban_butt,
            )
    except UserNotParticipant:
        try:
            await fallen.edit_text(f"🔄 ᴍᴇɴɢᴜɴᴅᴀɴɢ {ASS_NAME} ᴋᴇ {message.chat.title}...")
            join_success = False
            if message.chat.username:
                try:
                    entity = await app2.get_entity(f"@{message.chat.username}")
                    await app2(JoinChannelRequest(entity))
                    join_success = True
                except Exception as e:
                    LOGGER.warning(f"JoinChannelRequest failed: {e}")
            else:
                try:
                    invitelink = await app.export_chat_invite_link(message.chat.id)
                    if invitelink.startswith("https://t.me/joinchat/"):
                        hash_part = invitelink.replace("https://t.me/joinchat/", "")
                        await app2(ImportChatInviteRequest(hash_part))
                        join_success = True
                    elif invitelink.startswith("https://t.me/+"):
                        hash_part = invitelink.replace("https://t.me/+", "")
                        await app2(ImportChatInviteRequest(hash_part))
                        join_success = True
                    else:
                        await app2.join_chat(invitelink)
                        join_success = True
                except Exception as e:
                    LOGGER.warning(f"ImportChatInviteRequest failed: {e}")
            if join_success:
                await asyncio.sleep(2)
                return await fallen.edit_text(
                    f"✅ {ASS_NAME} ᴛᴇʟᴀʜ ʙᴇʀʜᴀsɪʜ ᴅɪᴜɴᴅᴀɴɢ ᴋᴇ {message.chat.title}.\n\n"
                    f"ꜱɪʟᴀᴋᴀɴ ᴋᴇᴛɪᴋ ᴜʟᴀɴɢ `/play` ᴜɴᴛᴜᴋ ᴍᴇᴍᴜᴛᴀʀ ʟᴀɢᴜ."
                )
        except FloodWaitError as e:
            LOGGER.warning(f"Flood wait: {e}")
            await asyncio.sleep(e.seconds)
        except TelethonUserAlreadyParticipantError:
            pass
        except Exception as e:
            LOGGER.error(f"Auto invite failed: {e}")

        try:
            if message.chat.username:
                group_link = f"https://t.me/{message.chat.username}"
            else:
                group_link = await app.export_chat_invite_link(message.chat.id)
        except:
            group_link = f"https://t.me/{ASS_USERNAME}"

        return await fallen.edit_text(
            f"» ᴀssɪsᴛᴀɴᴛ @{ASS_USERNAME} ʙᴇʟᴜᴍ ʙᴇʀɢᴀʙᴜɴɢ ᴅɪ ɢʀᴜᴘ ɪɴɪ.\n\n"
            f"ᴛᴏʟᴏɴɢ ᴜɴᴅᴀɴɢ ᴀssɪsᴛᴀɴᴛ ᴛᴇʀʟᴇʙɪʜ ᴅᴀʜᴜʟᴜ ᴅᴇɴɢᴀɴ ᴄᴀʀᴀ:\n"
            f"1️⃣ ᴋʟɪᴋ ᴛᴏᴍʙᴇʟ ᴅɪ ʙᴀᴡᴀʜ\n"
            f"2️⃣ ᴘɪʟɪʜ ᴜɴᴛᴜᴋ ᴍᴇɴɢᴜɴᴅᴀɴɢ @{ASS_USERNAME} ᴋᴇ ɢʀᴜᴘ",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        text=f"✚ ᴜɴᴅᴀɴɢ {ASS_NAME}",
                        url=f"https://t.me/{ASS_USERNAME}?startgroup=join"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔗 ʟɪɴᴋ ᴜɴᴅᴀɴɢᴀɴ ɢʀᴜᴘ",
                        url=group_link
                    )
                ]
            ])
        )

    ruser = message.from_user.first_name
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message else None
    )
    url = get_url(message)

    last_progress = {"percent": 0}

    async def update_progress(percent, speed):
        if percent - last_progress["percent"] >= 3 or percent == 100:
            last_progress["percent"] = percent
            try:
                await fallen.edit_text(
                    f"⬇️ **ᴍᴇɴɢᴜɴᴅᴜʜ...**\n"
                    f"**ᴘʀᴏɢʀᴇs :** `{percent:.1f}%`\n"
                    f"**sᴘᴇᴇᴅ :** `{speed}`"
                )
            except Exception:
                pass

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            return await fallen.edit_text(
                f"» ᴅᴜʀᴀsɪ ᴛʀᴀᴋ ᴍᴇʟᴇʙɪʜɪ {DURATION_LIMIT} ᴍᴇɴɪᴛ."
            )
        file_name = get_file_name(audio)
        title = file_name
        duration = round(audio.duration / 60)
        file_path = (
            await message.reply_to_message.download(file_name)
            if not os.path.isfile(os.path.join("downloads", file_name))
            else f"downloads/{file_name}"
        )
        videoid = "audio_reply"

    elif url:
        try:
            if is_playlist_url(url):
                await fallen.edit_text("📋 **Mendeteksi playlist...**")
                playlist_videos = get_playlist_videos(url, limit=10)

                if not playlist_videos:
                    raise Exception("Gagal mengambil daftar playlist")

                await fallen.edit_text(f"📋 **Menambahkan {len(playlist_videos)} lagu dari playlist...**")

                chat_active = await is_active_chat(message.chat.id)
                first_video = True
                added_count = 0

                for video in playlist_videos:
                    title = video['title']
                    duration_sec = video.get('duration', 0)
                    duration_min = round(duration_sec / 60)
                    videoid = video['id']
                    video_url = video['url']

                    if duration_min > DURATION_LIMIT:
                        continue

                    try:
                        file_path = audio_dl(video_url)
                        if not file_path:
                            continue

                        if chat_active and not first_video:
                            await put(
                                message.chat.id, title, duration_min, videoid, file_path, ruser,
                                message.from_user.id
                            )
                            added_count += 1
                        else:
                            stream = MediaStream(file_path)
                            try:
                                await pytgcalls.play(message.chat.id, stream)
                                await stream_on(message.chat.id)
                                await add_active_chat(message.chat.id)
                                chat_active = True
                                first_video = False

                                imgt = await gen_thumb(videoid, message.from_user.id)
                                await fallen.delete()
                                await message.reply_photo(
                                    photo=imgt,
                                    caption=f"**➻ ᴍᴇᴍᴜʟᴀɪ ᴘᴇᴍᴜᴛᴀʀᴀɴ**\n\n"
                                            f"‣ **ᴊᴜᴅᴜʟ :** [{title[:27]}](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n"
                                            f"‣ **ᴅᴜʀᴀsɪ :** `{duration_min}` ᴍᴇɴɪᴛ\n"
                                            f"‣ **ᴅɪᴍɪɴᴛᴀ ᴏʟᴇʜ :** {ruser}",
                                    reply_markup=buttons,
                                )
                                fallen = await message.reply_text("📋 **Menambahkan sisa playlist ke antrian...**")
                            except Exception as e:
                                LOGGER.error(f"Play first video error: {e}")
                                continue
                    except Exception as e:
                        LOGGER.error(f"Process playlist video error: {e}")
                        continue

                if added_count > 0:
                    await fallen.edit_text(f"✅ **{added_count} lagu ditambahkan ke antrian dari playlist.**")
                else:
                    await fallen.delete()
                return

            # BUKAN PLAYLIST -> single video
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Gagal mengambil info video")
                title = info.get('title', 'Unknown')
                duration_sec = info.get('duration', 0)
                duration_min = round(duration_sec / 60)
                videoid = info.get('id', '')
                if not videoid:
                    videoid = 'url_track'

            if duration_min > DURATION_LIMIT:
                return await fallen.edit_text(
                    f"» ᴅᴜʀᴀsɪ ᴛʀᴀᴋ ᴍᴇʟᴇʙɪʜɪ {DURATION_LIMIT} ᴍᴇɴɪᴛ."
                )

            await fallen.edit_text("⬇️ **ᴍᴇɴɢᴜɴᴅᴜʜ ᴀᴜᴅɪᴏ...**")
            file_path = await asyncio.get_running_loop().run_in_executor(
                None,
                audio_dl_progress,
                url,
                update_progress
            )
            if not file_path:
                raise Exception("Gagal mendownload audio")

        except Exception as e:
            LOGGER.error(f"URL processing error: {e}")
            return await fallen.edit_text(
                f"» ɢᴀɢᴀʟ ᴍᴇᴍᴘʀᴏsᴇs URL.\n\n**Error:** `{str(e)[:100]}`"
            )

    else:
        if len(message.command) < 2:
            return await fallen.edit_text("» ᴍᴀsᴜᴋᴋᴀɴ ᴊᴜᴅᴜʟ ᴀᴛᴀᴜ URL ʟᴀɢᴜ.")

        query = message.text.split(None, 1)[1]
        try:
            await fallen.edit_text("🔎")
            result = search_youtube(query)
            if not result:
                raise Exception("Tidak ditemukan")
            title = result['title']
            duration_sec = result['duration'] or 0
            duration_min = round(duration_sec / 60)
            videoid = result['id']
            url = result['url']

            if duration_min > DURATION_LIMIT:
                return await fallen.edit_text(
                    f"» ᴅᴜʀᴀsɪ ᴛʀᴀᴋ ᴍᴇʟᴇʙɪʜɪ {DURATION_LIMIT} ᴍᴇɴɪᴛ."
                )
        except Exception as e:
            LOGGER.error(str(e))
            return await fallen.edit_text(
                f"» ɢᴀɢᴀʟ ᴍᴇᴍᴘʀᴏsᴇs ᴘᴇʀᴍɪɴᴛᴀᴀɴ.\n\n**Error:** `{str(e)[:100]}`"
            )

        try:
            await fallen.edit_text("⬇️ **ᴍᴇɴɢᴜɴᴅᴜʜ ᴀᴜᴅɪᴏ...**")
            file_path = await asyncio.get_running_loop().run_in_executor(
                None,
                audio_dl_progress,
                url,
                update_progress
            )
            if not file_path:
                raise Exception("Gagal mendownload audio")
        except Exception as e:
            LOGGER.error(f"Download error: {e}")
            return await fallen.edit_text(
                f"» ɢᴀɢᴀʟ ᴍᴇɴɢᴜɴᴅᴜʜ ʟᴀɢᴜ.\n\n**Error:** `{str(e)[:100]}`"
            )

    chat_active = await is_active_chat(message.chat.id)

    if chat_active:
        await add_active_chat(message.chat.id)
        await put(
            message.chat.id, title, duration_min, videoid, file_path, ruser,
            message.from_user.id
        )
        position = len(novadb.get(message.chat.id, []))
        qimg = await gen_qthumb(videoid, message.from_user.id)
        await fallen.delete()
        await message.reply_photo(
            photo=qimg,
            caption=f"**➻ ᴅɪᴛᴀᴍʙᴀʜᴋᴀɴ ᴋᴇ ᴀɴᴛʀɪᴀɴ #{position}**\n\n"
                    f"‣ **ᴊᴜᴅᴜʟ :** [{title[:27]}](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n"
                    f"‣ **ᴅᴜʀᴀsɪ :** `{duration_min}` ᴍᴇɴɪᴛ\n"
                    f"‣ **ᴅɪᴍɪɴᴛᴀ ᴏʟᴇʜ :** {ruser}",
            reply_markup=buttons,
        )
    else:
        stream = MediaStream(file_path)
        try:
            await pytgcalls.play(message.chat.id, stream)
        except NoActiveGroupCall:
            return await fallen.edit_text(
                "**» ᴛɪᴅᴀᴋ ᴀᴅᴀ ᴠɪᴅᴇᴏᴄʜᴀᴛ ᴀᴋᴛɪғ.**\n\n"
                "ᴍᴜʟᴀɪ ᴠɪᴅᴇᴏᴄʜᴀᴛ ᴛᴇʀʟᴇʙɪʜ ᴅᴀʜᴜʟᴜ."
            )
        except Exception as e:
            LOGGER.error(e)
            await fallen.edit_text(f"» ɢᴀɢᴀʟ ᴍᴀsᴜᴋ ᴠɪᴅᴇᴏᴄʜᴀᴛ:\n`{str(e)[:100]}`")
            return

        await stream_on(message.chat.id)
        await add_active_chat(message.chat.id)

        imgt = await gen_thumb(videoid, message.from_user.id)
        await fallen.delete()
        await message.reply_photo(
            photo=imgt,
            caption=f"**➻ ᴍᴇᴍᴜʟᴀɪ ᴘᴇᴍᴜᴛᴀʀᴀɴ**\n\n"
                    f"‣ **ᴊᴜᴅᴜʟ :** [{title[:27]}](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n"
                    f"‣ **ᴅᴜʀᴀsɪ :** `{duration_min}` ᴍᴇɴɪᴛ\n"
                    f"‣ **ᴅɪᴍɪɴᴛᴀ ᴏʟᴇʜ :** {ruser}",
            reply_markup=buttons,
        )

    try:
        await fallen.delete()
    except:
        pass
