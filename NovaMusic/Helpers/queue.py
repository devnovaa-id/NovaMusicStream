from NovaMusic import novadb


async def put(
    chat_id,
    title,
    duration,
    videoid,
    file_path,
    ruser,
    user_id,
    is_video=False,  # tambahan
):
    put_f = {
        "title": title,
        "duration": duration,
        "file_path": file_path,
        "videoid": videoid,
        "req": ruser,
        "user_id": user_id,
        "is_video": is_video,  # simpan flag
    }
    get = novadb.get(chat_id)
    if get:
        novadb[chat_id].append(put_f)
    else:
        novadb[chat_id] = []
        novadb[chat_id].append(put_f)
