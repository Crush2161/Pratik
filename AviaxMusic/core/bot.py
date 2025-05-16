import sys
from typing import Optional

if sys.platform != "win32":
    import uvloop
    uvloop.install()

from pyrogram.client import Client
from pyrogram import errors
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import User

import config
from ..logging import LOGGER


class Aviax(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")
        
        # Verify required configs
        if not config.API_ID or not config.API_HASH or not config.BOT_TOKEN:
            LOGGER(__name__).error("Required configs missing! Please check config.py")
            sys.exit(1)
            
        super().__init__(
            name="AviaxMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.HTML,
        )
        
        self.username: Optional[str] = None
        self.id: Optional[int] = None
        self.name: Optional[str] = None
        self.mention: Optional[str] = None

    async def start(self) -> "Aviax":
        """Start the bot and set up its attributes"""
        await super().start()
        self.me = await self.get_me()
        
        self.id = self.me.id
        self.username = self.me.username
        self.mention = self.me.mention
        self.name = f"{self.me.first_name} {self.me.last_name or ''}"
        
        try:
            await self.send_message(
                config.LOG_GROUP_ID,
                f"» {self.mention} Bot started!"
            )
        except errors.ChatWriteForbidden:
            LOGGER(__name__).error("Bot does not have write permission in LOG_GROUP_ID")
        except errors.ChannelInvalid:
            LOGGER(__name__).error("LOG_GROUP_ID is invalid or bot is not a member")
        except Exception as e:
            LOGGER(__name__).error(f"Failed to send startup message: {str(e)}")
            
        LOGGER(__name__).info(f"Music Bot Started as {self.name}")
        return self

    async def stop(self, block: bool = True) -> "Aviax":
        """Stop the bot"""
        await super().stop(block=block)
        LOGGER(__name__).info("Music Bot Stopped, Bye!")
        return self
