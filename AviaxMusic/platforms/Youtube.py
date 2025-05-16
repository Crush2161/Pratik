import asyncio
import os
import re
import glob
import random
from typing import Union, Optional, Dict, Any
import yt_dlp

def cookie_txt_file() -> Optional[str]:
    """Get a random cookie file from cookies directory"""
    cookie_files = glob.glob("cookies/*.txt")
    return random.choice(cookie_files) if cookie_files else None

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"

    async def exists(self, link: str) -> bool:
        """Check if link is valid YouTube URL"""
        return bool(re.search(self.regex, link))

    async def get_video_info(self, link: str) -> Dict[str, Any]:
        """Get basic video information"""
        if "&" in link:
            link = link.split("&")[0]
        
        def _get_info() -> Dict[str, Any]:
            ydl_opts: Dict[str, Any] = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": True
            }
            if cookie_path := cookie_txt_file():
                ydl_opts["cookiefile"] = cookie_path
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(link, download=False)
        
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, _get_info)
        
        return {
            "title": info.get("title", ""),
            "duration": info.get("duration", 0),
            "thumbnail": info.get("thumbnail", ""),
            "id": info.get("id", ""),
            "url": info.get("webpage_url", link)
        }

    async def download(self, link: str, video: bool = False) -> str:
        """Download YouTube video/audio"""
        if "&" in link:
            link = link.split("&")[0]
        
        def _download() -> str:
            ydl_opts: Dict[str, Any] = {
                "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best" if video else "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True
            }
            if cookie_path := cookie_txt_file():
                ydl_opts["cookiefile"] = cookie_path
                
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            info = ydl.extract_info(link, download=True)
            return os.path.join("downloads", f"{info['id']}.{info['ext']}")
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _download)

    async def stream_url(self, link: str) -> Optional[str]:
        """Get direct stream URL"""
        if "&" in link:
            link = link.split("&")[0]
            
        cmd = ["yt-dlp", "-g", "-f", "best[height<=720]/best", link]
        if cookie_path := cookie_txt_file():
            cmd.extend(["--cookies", cookie_path])
            
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode().strip() if stdout else None
