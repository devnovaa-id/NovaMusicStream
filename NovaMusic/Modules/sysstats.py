
import asyncio
import os
import platform
import re
import socket
import time
import uuid
from sys import version as pyver

import psutil
from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls.__version__ import __version__ as pytgver

from NovaMusic import BOT_NAME, SUDOERS, StartTime, app
from NovaMusic.Modules import ALL_MODULES


def _human_uptime(seconds: float) -> str:
    seconds = int(seconds)
    d, seconds = divmod(seconds, 86400)
    h, seconds = divmod(seconds, 3600)
    m, s = divmod(seconds, 60)
    if d:
        return f"{d}d {h}h {m}m"
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def _human_bytes(num: float) -> str:
    num = float(num)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num) < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"


def _cpu_model() -> str:
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    m = platform.processor()
    return m or "unknown"


@app.on_message(filters.command(["stats", "sysstats"]) & SUDOERS)
async def sys_stats(_, message: Message):
    sysrep = await message.reply_text(
        f"ɢᴇᴛᴛɪɴɢ {BOT_NAME} sʏsᴛᴇᴍ sᴛᴀᴛs, ɪᴛ'ʟʟ ᴛᴀᴋᴇ ᴀ ᴡʜɪʟᴇ..."
    )
    try:
        await message.delete()
    except Exception:
        pass

    sudoers = len(SUDOERS)
    mod = len(ALL_MODULES)
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(socket.gethostname())
    architecture = platform.machine()
    mac_address = ":".join(re.findall("..", "%012x" % uuid.getnode()))
    sp = platform.system()
    platform_release = platform.release()
    platform_version = platform.version()

    cpu_model = _cpu_model()
    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    try:
        cpu_freq = psutil.cpu_freq().current
        if cpu_freq >= 1000:
            cpu_freq = f"{round(cpu_freq / 1000, 2)}ɢʜᴢ"
        else:
            cpu_freq = f"{round(cpu_freq, 2)}ᴍʜᴢ"
    except Exception:
        cpu_freq = "ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ"

    # CPU usage (di executor agar tidak memblok event loop / audio).
    loop = asyncio.get_event_loop()
    try:
        cpu_usage = f"{await loop.run_in_executor(None, lambda: psutil.cpu_percent(interval=0.5)):.1f}%"
    except Exception:
        cpu_usage = "N/A"

    # RAM.
    vmem = psutil.virtual_memory()
    ram = f"{round(vmem.used / (1024.0**3))}/{round(vmem.total / (1024.0**3))} ɢʙ ({vmem.percent}%)"

    # Storage.
    hdd = psutil.disk_usage("/")
    total = f"{hdd.total / (1024.0**3):.0f}"
    used = f"{hdd.used / (1024.0**3):.0f}"
    free = f"{hdd.free / (1024.0**3):.0f}"

    # Uptime.
    bot_uptime = _human_uptime(time.time() - StartTime)
    try:
        sys_uptime = _human_uptime(time.time() - psutil.boot_time())
    except Exception:
        sys_uptime = "N/A"

    # Load average.
    try:
        la = os.getloadavg()
        load_avg = f"{la[0]:.2f} / {la[1]:.2f} / {la[2]:.2f}"
    except Exception:
        load_avg = "N/A"

    # Processes & Network I/O.
    try:
        proc_count = len(psutil.pids())
    except Exception:
        proc_count = "N/A"
    try:
        net = psutil.net_io_counters()
        net_io = f"\u2193 {_human_bytes(net.bytes_recv)} / \u2191 {_human_bytes(net.bytes_sent)}"
    except Exception:
        net_io = "N/A"

    await sysrep.edit_text(
        f"""
➻ <u>**{BOT_NAME} sʏsᴛᴇᴍ sᴛᴀᴛs**</u>

**ᴩʏᴛʜᴏɴ :** {pyver.split()[0]}
**ᴩʏʀᴏɢʀᴀᴍ :** {pyrover}
**ᴩʏ-ᴛɢᴄᴀʟʟs :** {pytgver}
**sᴜᴅᴏᴇʀs :** `{sudoers}`
**ᴍᴏᴅᴜʟᴇs :** `{mod}`
**ʙᴏᴛ ᴜᴘᴛɪᴍᴇ :** `{bot_uptime}`
**sʏsᴛᴇᴍ ᴜᴘᴛɪᴍᴇ :** `{sys_uptime}`

**ɪᴘ :** ||{ip_address}||
**ᴍᴀᴄ :** ||{mac_address}||
**ʜᴏsᴛɴᴀᴍᴇ :** ||{hostname}||
**ᴘʟᴀᴛғᴏʀᴍ :** {sp}
**ᴄᴘᴜ ᴍᴏᴅᴇʟ :** {cpu_model}
**ᴀʀᴄʜɪᴛᴇᴄᴛᴜʀᴇ :** {architecture}
**ᴄᴘᴜ ᴜsᴀɢᴇ :** `{cpu_usage}`
**ᴘʜʏsɪᴄᴀʟ ᴄᴏʀᴇs :** `{p_core}`
**ᴛᴏᴛᴀʟ ᴄᴏʀᴇs :** `{t_core}`
**ᴄᴘᴜ ғʀᴇǫᴜᴇɴᴄʏ :** `{cpu_freq}`
**ʟᴏᴀᴅ ᴀᴠᴇʀᴀɢᴇ :** `{load_avg}`
**ᴘʟᴀᴛғᴏʀᴍ ʀᴇʟᴇᴀsᴇ :** {platform_release}
**ᴘʟᴀᴛғᴏʀᴍ ᴠᴇʀsɪᴏɴ :** {platform_version}

<u>**sᴛᴏʀᴀɢᴇ**</u>
**ᴀᴠᴀɪʟᴀʙʟᴇ :** {total} ɢɪʙ
**ᴜsᴇᴅ :** {used} ɢɪʙ
**ғʀᴇᴇ :** {free} ɢɪʙ

**ʀᴀᴍ :** `{ram}`
**ᴘʀᴏᴄᴇssᴇs :** `{proc_count}`
**ɴᴇᴛᴡᴏʀᴋ :** `{net_io}`""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="ᴄʟᴏsᴇ",
                        callback_data=f"forceclose abc|{message.from_user.id}",
                    ),
                ]
            ]
        ),
    )
