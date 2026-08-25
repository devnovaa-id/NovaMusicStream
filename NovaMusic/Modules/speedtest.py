
import asyncio

import speedtest
from pyrogram import filters

from NovaMusic import LOGGER, SUDOERS, app

logger = LOGGER


def testspeed(m):
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        m = m.edit("**⇆ ʀᴜɴɴɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ sᴘᴇᴇᴅᴛᴇsᴛ...**")
        test.download()
        m = m.edit("**⇆ ʀᴜɴɴɪɴɢ ᴜᴘʟᴏᴀᴅ sᴘᴇᴇᴅᴛᴇsᴛ...**")
        test.upload()
        result = test.results.dict()
        # Screenshot submission ke speedtest.net bisa gagal (server-side / network).
        # Jangan fatal — tetap kembalikan hasil, hanya tanpa gambar.
        try:
            result["share"] = test.results.share()
        except Exception as e:
            logger.warning(f"Speedtest share() failed (non-fatal): {e}")
            result["share"] = None
        m = m.edit("**↻ sʜᴀʀɪɴɢ sᴘᴇᴇᴅᴛᴇsᴛ ʀᴇsᴜʟᴛs...**")
        return result
    except Exception as e:
        logger.error(f"Speedtest failed: {e}")
        return None


@app.on_message(filters.command(["speedtest", "spt"]) & SUDOERS)
async def speedtest_function(_, message):
    m = await message.reply_text("**» ʀᴜɴɴɪɴɢ sᴘᴇᴇᴅᴛᴇsᴛ...**")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, testspeed, m)
    if not isinstance(result, dict):
        try:
            return await m.edit("**» sᴘᴇᴇᴅᴛᴇsᴛ ɢᴀɢᴀʟ, ᴛɪᴅᴀᴋ ᴅᴀᴘᴀᴛ ᴍᴇɴɢᴀᴍʙɪʟ ʜᴀsɪʟ.**")
        except Exception:
            return
    output = f"""✯ **sᴘᴇᴇᴅᴛᴇsᴛ ʀᴇsᴜʟᴛs** ✯

<u>**❥͜͡ᴄʟɪᴇɴᴛ :**</u>
**» __ɪsᴘ :__** {result.get('client', {}).get('isp', 'N/A')}
**» __ᴄᴏᴜɴᴛʀʏ :__** {result.get('client', {}).get('country', 'N/A')}

<u>**❥͜͡sᴇʀᴠᴇʀ :**</u>
**» __ɴᴀᴍᴇ :__** {result.get('server', {}).get('name', 'N/A')}
**» __ᴄᴏᴜɴᴛʀʏ :__** {result.get('server', {}).get('country', 'N/A')}, {result.get('server', {}).get('cc', 'N/A')}
**» __sᴘᴏɴsᴏʀ :__** {result.get('server', {}).get('sponsor', 'N/A')}
**» __ʟᴀᴛᴇɴᴄʏ :__** {result.get('server', {}).get('latency', 'N/A')}
    **» __ᴘɪɴɢ :__** {result.get('ping', 'N/A')}"""
    share = result.get("share")
    try:
        if share:
            await app.send_photo(
                chat_id=message.chat.id, photo=share, caption=output
            )
        else:
            await app.send_message(
                chat_id=message.chat.id, text=output
            )
        await m.delete()
    except Exception as e:
        logger.error(f"Send speedtest result failed: {e}")
        try:
            await m.edit(output or "**» ɢᴀɢᴀʟ ᴍᴇɴɢɪʀɪᴍ ʜᴀsɪʟ sᴘᴇᴇᴅᴛᴇsᴛ.**")
        except Exception:
            pass
