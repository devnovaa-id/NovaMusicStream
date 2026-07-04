
from NovaMusic import novadb
from NovaMusic.Helpers import remove_active_chat


async def _clear_(chat_id):
    try:
        novadb[chat_id] = []
        await remove_active_chat(chat_id)
    except:
        return
