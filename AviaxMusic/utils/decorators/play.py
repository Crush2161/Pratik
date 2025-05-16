import asyncio

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from AviaxMusic import YouTube, app
from AviaxMusic.misc import SUDOERS
from AviaxMusic.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_maintenance,
)
from AviaxMusic.utils.inline import botplaylist_markup
from config import PLAYLIST_IMG_URL, SUPPORT_GROUP, adminlist
from strings import get_string

invite_links = {}


def PlayWrapper(command):
    async def wrapper(client, message):
        lang_code = await get_lang(message.chat.id)
        _ = get_string(lang_code)

        if message.sender_chat:
            return await message.reply_text(
                _["general_3"],
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("ʜᴏᴡ ᴛᴏ ғɪx ?", callback_data="AnonymousAdmin")]]
                ),
            )

        if not await is_maintenance() and message.from_user.id not in SUDOERS:
            return await message.reply_text(
                f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ <a href={SUPPORT_GROUP}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴜᴘᴅᴀᴛᴇs.",
                disable_web_page_preview=True,
            )

        try:
            await message.delete()
        except:
            pass

        audio = (
            message.reply_to_message.audio or message.reply_to_message.voice
            if message.reply_to_message
            else None
        )
        video = (
            message.reply_to_message.video or message.reply_to_message.document
            if message.reply_to_message
            else None
        )
        url = await YouTube.url(message)

        if not audio and not video and not url:
            if len(message.command) < 2:
                if "stream" in message.command:
                    return await message.reply_text(_["str_1"])
                return await message.reply_photo(
                    PLAYLIST_IMG_URL,
                    caption=_["play_18"],
                    reply_markup=InlineKeyboardMarkup(botplaylist_markup(_)),
                )

        # Determine chat ID and playback mode
        if message.command[0].startswith("c"):
            chat_id = await get_cmode(message.chat.id)
            if not chat_id:
                return await message.reply_text(_["setting_7"])
            try:
                channel = (await app.get_chat(chat_id)).title
            except:
                return await message.reply_text(_["cplay_4"])
        else:
            chat_id = message.chat.id
            channel = None

        playmode = await get_playmode(chat_id)
        playtype = await get_playtype(chat_id)

        # Check permissions
        if playtype != "Everyone" and message.from_user.id not in SUDOERS:
            admins = adminlist.get(chat_id)
            if not admins or message.from_user.id not in admins:
                return await message.reply_text(_["play_4"] if admins else _["admin_13"])

        video_mode = (
            True
            if message.command[0].startswith("v")
            or "-v" in message.text
            or message.command[0][1:2] == "v"
            else None
        )
        force_play = message.command[0].endswith("e")

        # Assistant join if inactive
        if not await is_active_chat(chat_id):
            assistant = await get_assistant(chat_id)
            try:
                try:
                    member = await app.get_chat_member(chat_id, assistant.id)
                except ChatAdminRequired:
                    return await message.reply_text(_["call_1"])

                if member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                    return await message.reply_text(
                        _["call_2"].format(
                            app.mention, assistant.id, assistant.name, assistant.username
                        )
                    )
            except UserNotParticipant:
                invite_link = invite_links.get(chat_id)
                if not invite_link:
                    if message.chat.username:
                        invite_link = message.chat.username
                        try:
                            await assistant.resolve_peer(invite_link)
                        except:
                            pass
                    else:
                        try:
                            invite_link = await app.export_chat_invite_link(chat_id)
                        except ChatAdminRequired:
                            return await message.reply_text(_["call_1"])
                        except Exception as e:
                            return await message.reply_text(
                                _["call_3"].format(app.mention, type(e).__name__)
                            )

                if invite_link.startswith("https://t.me/+"):
                    invite_link = invite_link.replace("https://t.me/+", "https://t.me/joinchat/")

                invite_links[chat_id] = invite_link
                notice = await message.reply_text(_["call_4"].format(app.mention))

                try:
                    await asyncio.sleep(1)
                    await assistant.join_chat(invite_link)
                except InviteRequestSent:
                    try:
                        await app.approve_chat_join_request(chat_id, assistant.id)
                    except Exception as e:
                        return await message.reply_text(
                            _["call_3"].format(app.mention, type(e).__name__)
                        )
                    await asyncio.sleep(2)
                    await notice.edit(_["call_5"].format(app.mention))
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    return await message.reply_text(
                        _["call_3"].format(app.mention, type(e).__name__)
                    )

                try:
                    await assistant.resolve_peer(chat_id)
                except:
                    pass

        return await command(
            client,
            message,
            _,
            chat_id,
            video_mode,
            channel,
            playmode,
            url,
            force_play,
        )

    return wrapper
