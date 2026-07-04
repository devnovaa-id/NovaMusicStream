
from NovaMusic import novadb


async def put(
    chat_id,
    title,
    duration,
    videoid,
    file_path,
    ruser,
    user_id,
):
    put_f = {
        "title": title,
        "duration": duration,
        "file_path": file_path,
        "videoid": videoid,
        "req": ruser,
        "user_id": user_id,
    }
    get = novadb.get(chat_id)
    if get:
        novadb[chat_id].append(put_f)
    else:
        novadb[chat_id] = []
        novadb[chat_id].append(put_f)
