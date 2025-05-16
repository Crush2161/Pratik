"""
Simple YouTube music player with basic controls
"""

from pyrogram import filters
from pyrogram.types import Message

from ... import app
from ...core.call import Aviax
from ...utils.stream.simple_stream import stream, skip_stream

@app.on_message(
    filters.command(["play", "vplay"]) 
    & filters.group
)
async def play_track(_, message: Message):
    """Play YouTube audio/video in voice chat"""
    if len(message.command) < 2:
        return await message.reply_text("❌ Please provide a YouTube URL or search query.")
    
    status = await message.reply_text("🔄 Processing...")
    
    try:
        query = message.text.split(None, 1)[1]
        video_mode = message.command[0].startswith("v")
        
        result = await stream(message, query, video_mode)
        if not result:
            await status.edit_text("❌ Could not process this request.")
            return
            
        await status.edit_text(
            f"🎵 **{'Added to Queue' if 'position' in result else 'Now Playing'}**\n"
            f"**Title:** {result['title']}\n"
            f"**Duration:** {result['duration']} seconds\n"
            f"**Requested By:** {result['requested_by']}\n"
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
    """Skip to next track"""
    try:
        next_track = await skip_stream(message.chat.id)
        if next_track:
            await message.reply_text(
                f"⏭️ **Skipped to Next Track**\n"
                f"**Title:** {next_track['title']}\n"
                f"**Mode:** {'Video' if next_track['video'] else 'Audio'}"
            )
        else:
            await message.reply_text("⏹️ No more tracks in queue")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
