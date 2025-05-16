"""
Simple YouTube music player with basic controls
"""

from pyrogram import filters
from pyrogram.types import Message

from ... import app
from ...platforms.Youtube import YouTubeAPI
from ...core.call import Aviax

# Initialize YouTube API
youtube = YouTubeAPI()

@app.on_message(
    filters.command(["play", "vplay"]) 
    & filters.group
)
async def play_track(_, message: Message):
    """Play YouTube audio/video in voice chat"""
    chat_id = message.chat.id
    
    if len(message.command) < 2:
        return await message.reply_text("❌ Please provide a YouTube URL or search query.")
    
    status = await message.reply_text("🔄 Processing...")
    
    try:
        query = message.text.split(None, 1)[1]
        video_mode = message.command[0].startswith("v")
        
        # Get video info
        info = await youtube.get_video_info(query)
        if not info.get("id"):
            await status.edit_text("❌ No matching video found")
            return
            
        # Get stream URL
        stream_url = await youtube.stream_url(info["url"])
        if not stream_url:
            await status.edit_text("❌ Could not get playable URL")
            return
            
        # Join and play
        await Aviax.join_group_call(
            chat_id,
            stream_url,
            video=video_mode
        )
        
        await status.edit_text(
            f"🎵 **Now Playing**\n"
            f"**Title:** {info['title']}\n"
            f"**Mode:** {'Video' if video_mode else 'Audio'}"
        )
            
    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}")

@app.on_message(
    filters.command("pause") 
    & filters.group
)
async def pause_stream(_, message: Message):
    """Pause the current playing track"""
    try:
        await Aviax.pause_stream(message.chat.id)
        await message.reply_text("⏸️ Stream paused")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@app.on_message(
    filters.command("resume") 
    & filters.group
)
async def resume_stream(_, message: Message):
    """Resume the paused track"""
    try:
        await Aviax.resume_stream(message.chat.id)
        await message.reply_text("▶️ Stream resumed")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@app.on_message(
    filters.command("stop") 
    & filters.group
)
async def stop_stream(_, message: Message):
    """Stop the current stream and leave voice chat"""
    try:
        await Aviax.leave_group_call(message.chat.id)
        await message.reply_text("⏹️ Stream stopped")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@app.on_message(
    filters.command(["next", "skip"])
    & filters.group
)
async def skip_track(_, message: Message):
    """Skip to next track (same as stop for single track)"""
    try:
        await Aviax.leave_group_call(message.chat.id)
        await message.reply_text("⏭️ Track skipped")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
