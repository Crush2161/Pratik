from functools import wraps
from strings import get_string
from AviaxMusic.utils.database import get_lang


def language(mystic):
    @wraps(mystic)
    async def wrapper(_, message, **kwargs):
        chat_id = message.chat.id if hasattr(message, "chat") else message.from_user.id
        try:
            language = await get_lang(chat_id)
            language = get_string(language)
        except:
            language = get_string("en")
        return await mystic(_, message, language, **kwargs)

    return wrapper


def languageCB(mystic):
    @wraps(mystic)
    async def wrapper(_, CallbackQuery, **kwargs):
        chat_id = CallbackQuery.message.chat.id
        try:
            language = await get_lang(chat_id)
            language = get_string(language)
        except:
            language = get_string("en")
        return await mystic(_, CallbackQuery, language, **kwargs)

    return wrapper
