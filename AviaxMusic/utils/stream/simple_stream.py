"""
Simple streaming implementation for YouTube
Handles basic playback and queue management
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pyrogram.types import Message

from ...platforms.Youtube import YouTubeAPI
from ...core.call import Aviax
from ...misc import db

youtube = YouTubeAPI()

@dataclass
class StreamInfo:
    """Information about a stream"""
    chat_id: int
    stream_url: str
    title: str
    duration: int
    video: bool
    requested_by: str
    position: Optional[int] = None

async def stream(
    message: Message,
    query: str,
    video_mode: bool = False
) -> Optional[StreamInfo]:
    """
    Stream from YouTube
    
    Args:
        message: The message containing the command
        query: YouTube URL or search query
        video_mode: Whether to stream video
        
    Returns:
        StreamInfo object if successful, None otherwise
    """
    try:
        # Get video info
        info = await youtube.get_video_info(query)
        if not info.get("id"):
            return None
            
        # Get stream URL
        stream_url = await youtube.stream_url(info["url"])
        if not stream_url:
            return None
            
        # Prepare stream info
        chat_id = message.chat.id
        queue: List[StreamInfo] = db.get(chat_id, [])
        
        stream_info = StreamInfo(
            chat_id=chat_id,
            stream_url=stream_url,
            title=info["title"],
            duration=info.get("duration", 0),
            video=video_mode,
            requested_by=message.from_user.mention if message.from_user else "Unknown",
            position=len(queue) if queue else None
        )
        
        if not queue:  # Play immediately if queue is empty
            await Aviax.join_group_call(
                chat_id,
                stream_url,
                video=video_mode
            )
        else:  # Add to queue
            queue.append(stream_info)
            db[chat_id] = queue
            
        return stream_info
            
    except Exception as e:
        print(f"Stream error: {str(e)}")
        return None

async def skip_stream(chat_id: int) -> Optional[StreamInfo]:
    """
    Skip current stream and play next in queue
    
    Args:
        chat_id: The chat ID where to skip
        
    Returns:
        StreamInfo of next track if available, None otherwise
    """
    try:
        queue: List[StreamInfo] = db.get(chat_id, [])
        
        # Stop current stream
        await Aviax.leave_group_call(chat_id)
        
        # Play next if available
        if queue:
            next_stream = queue.pop(0)
            db[chat_id] = queue
            
            await Aviax.join_group_call(
                chat_id,
                next_stream.stream_url,
                video=next_stream.video
            )
            return next_stream
            
        return None
        
    except Exception as e:
        print(f"Skip error: {str(e)}")
        return None
