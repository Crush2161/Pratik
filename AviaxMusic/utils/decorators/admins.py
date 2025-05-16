from typing import Dict, List, Union

from AviaxMusic import app
from AviaxMusic.misc import SUDOERS
from AviaxMusic.utils.database import get_authuser_names, is_active_chat
from strings import get_string
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.types import Message

from ..formatters import int_to_alpha

def AdminRightsCheck(mystic):
    async def wrapper(client, message: Message):
        if message.sender_chat:
            return await message.reply_text(
                "You're an __Anonymous Admin__\nRevert back to User Account..."
            )
        is_non_admin = await is_active_chat(message.chat.id)
        if not is_non_admin:
            return await mystic(client, message)
        if message.from_user.id in SUDOERS:
            return await mystic(client, message)
        try:
            member = await app.get_chat_member(message.chat.id, message.from_user.id)
        except:
            return
        if not member.can_manage_voice_chats:
            return await message.reply(
                "You don't have the required permissions to perform this action.\n\n__REQUIRES VOICE CHAT ADMIN__"
            )
        return await mystic(client, message)
    return wrapper

def AdminActual(mystic):
    async def wrapper(client, message: Message):
        if message.sender_chat:
            return await message.reply_text(
                "You're an __Anonymous Admin__\nRevert back to User Account..."
            )
        is_non_admin = await is_active_chat(message.chat.id)
        if not is_non_admin:
            return await mystic(client, message)
        if message.from_user.id in SUDOERS:
            return await mystic(client, message)
        try:
            member = await app.get_chat_member(message.chat.id, message.from_user.id)
        except:
            return
        if not member.can_manage_voice_chats:
            return await message.reply(
                "You don't have the required permissions to perform this action.\n\n__REQUIRES VOICE CHAT ADMIN__"
            )
        return await mystic(client, message)
    return wrapper

def AdminRightsCheckCB(mystic):
    async def wrapper(client, CallbackQuery):
        is_non_admin = await is_active_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            return await mystic(client, CallbackQuery)
        a = await app.get_chat_member(CallbackQuery.message.chat.id, CallbackQuery.from_user.id)
        if not a.can_manage_voice_chats:
            return await CallbackQuery.answer(
                "You don't have the required permissions to perform this action.\n\nPermission: MANAGE VOICE CHATS",
                show_alert=True,
            )
        return await mystic(client, CallbackQuery)
    return wrapper

def ActualAdminCB(mystic):
    async def wrapper(client, CallbackQuery):
        is_non_admin = await is_active_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            return await mystic(client, CallbackQuery)
        a = await app.get_chat_member(CallbackQuery.message.chat.id, CallbackQuery.from_user.id)
        if not a.can_manage_voice_chats:
            return await CallbackQuery.answer(
                "You don't have the required permissions to perform this action.\n\nPermission: MANAGE VOICE CHATS",
                show_alert=True,
            )
        return await mystic(client, CallbackQuery)
    return wrapper
