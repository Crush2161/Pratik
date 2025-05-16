import asyncio
from typing import Union

from AviaxMusic.misc import db
from AviaxMusic.utils.formatters import check_duration, seconds_to_min
from config import autoclean, time_to_seconds
from AviaxMusic.core.mongo import mongodb

queue_collection = mongodb.queue

async def save_queue_to_db(chat_id):
    try:
        if chat_id in db:
            await queue_collection.update_one(
                {"chat_id": chat_id},
                {"$set": {"queue": db[chat_id]}},
                upsert=True
            )
    except Exception as e:
        print(f"Error saving queue: {e}")

async def put_queue(
    chat_id,
    original_chat_id,
    file,
    title,
    duration,
    user,
    vidid,
    user_id,
    stream,
    forceplay: Union[bool, str] = None,
):
    title = title.title()
    try:
        duration_in_seconds = time_to_seconds(duration) - 3
    except:
        duration_in_seconds = 0
    put = {
        "title": title,
        "dur": duration,
        "streamtype": stream,
        "by": user,
        "user_id": user_id,
        "chat_id": original_chat_id,
        "file": file,
        "vidid": vidid,
        "seconds": duration_in_seconds,
        "played": 0,
    }
    if forceplay:
        check = db.get(chat_id)
        if check:
            check.insert(0, put)
        else:
            db[chat_id] = []
            db[chat_id].append(put)
    else:
        if chat_id not in db:
            db[chat_id] = []
        db[chat_id].append(put)
    
    # Save to MongoDB after modifying queue
    await save_queue_to_db(chat_id)
    
    if file not in autoclean:
        autoclean.append(file)


async def put_queue_index(
    chat_id,
    original_chat_id,
    file,
    title,
    duration,
    user,
    vidid,
    stream,
    forceplay: Union[bool, str] = None,
):
    if "20.212.146.162" in vidid:
        try:
            dur = await asyncio.get_event_loop().run_in_executor(
                None, check_duration, vidid
            )
            duration = seconds_to_min(dur)
        except:
            duration = "ᴜʀʟ sᴛʀᴇᴀᴍ"
            dur = 0
    else:
        dur = 0
    put = {
        "title": title,
        "dur": duration,
        "streamtype": stream,
        "by": user,
        "chat_id": original_chat_id,
        "file": file,
        "vidid": vidid,
        "seconds": dur,
        "played": 0,
    }
    if forceplay:
        check = db.get(chat_id)
        if check:
            check.insert(0, put)
        else:
            db[chat_id] = []
            db[chat_id].append(put)
    else:
        if chat_id not in db:
            db[chat_id] = []
        db[chat_id].append(put)
    
    # Save to MongoDB after modifying queue
    await save_queue_to_db(chat_id)
