# ================================================================
#  🧠 Project: BADMUSIC - YTAPI Module
#  📦 Repository: https://github.com/masoombalak88/BADMUSIC
#  💬 Chat Group: https://t.me/PBX_CHAT
#  📢 Updates Channel: https://t.me/PBX_UPDATE
#  👨‍💻 Developer: @BadMundaXD
#
#  © 2025 PBX | All Rights Reserved.
#  Unauthorized redistribution or modification of this code
#  without explicit permission from the author is strictly prohibited.
# ================================================================


import asyncio
import aiohttp
import os
import re
import json
import random
import glob
import logging
import urllib.parse
from typing import Union, Tuple, Optional

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from BADMUSIC import app
from BADMUSIC.utils.database import is_on_off
from BADMUSIC.utils.formatters import time_to_seconds
from .Youtube import YouTubeAPI


_cached_cookie = None
_info_cache = {}  

def cookie_txt_file():
    global _cached_cookie
    if _cached_cookie:
        return _cached_cookie

    folder_path = os.path.join(os.getcwd(), "cookies")
    log_filename = os.path.join(os.getcwd(), "cookies", "logs.csv")
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    chosen_file = random.choice(txt_files)
    with open(log_filename, 'a') as file:
        file.write(f'Choosen File : {chosen_file}\n')
    _cached_cookie = f"cookies/{os.path.basename(chosen_file)}"
    return _cached_cookie

def extract_video_info(link: str) -> dict:
    if link in _info_cache:
        return _info_cache[link]
    ytdl_opts = {
        "quiet": True,
        "cookiefile": cookie_txt_file(),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
    _info_cache[link] = info
    return info


async def fetch_song(query: str, streamtype: str = "audio") -> dict:
    api_url = "http://80.211.223.37:1470/youtube"
    api_key = "1a873582a7c83342f961xx0a177b2b26"
    
    # Check if it's a YouTube URL or search query
    youtube_regex = r"(?:youtube\.com|youtu\.be)"
    is_youtube_url = re.search(youtube_regex, query)
    
    # If it's not a YouTube URL, process it as a search query
    if not is_youtube_url:
        # Replace spaces with + and then URL encode
        search_query = query.replace(" ", "+")
        # URL encode any other special characters
        search_query = urllib.parse.quote_plus(search_query)
    else:
        # It's already a YouTube URL, use as is
        search_query = query
    
    async with aiohttp.ClientSession() as session:
        params = {
            "query": search_query,
            "api_key": api_key
        }
        try:
            async with session.get(api_url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return {"link": data.get("stream_url", "")}
        except Exception as e:
            print(f"Error calling YouTube API: {e}")
            return {"error": str(e)}

# =============================================


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = re.compile(r"(?:youtube\.com|youtu\.be)")
        self.listbase = "https://youtube.com/playlist?list="

    async def get_download_link(self, query: str, video_stream: bool = False) -> Tuple[Optional[str], Optional[str]]:
        streamtype = "video" if video_stream else "audio"
        song_data = await fetch_song(query, streamtype)

        if not song_data or "error" in song_data or "link" not in song_data:
            error_msg = song_data.get("error", "Failed to process query")
            return None, error_msg

        song_url = song_data["link"]
        return song_url, None

    async def exists(self, link: str, videoid: Union[bool, str] = None) -> bool:
        if videoid:
            link = self.base + link
        return bool(self.regex.search(link))

    async def url(self, message: Message) -> Union[str, None]:
        messages = [message]
        if message.reply_to_message:
            messages.append(message.reply_to_message)
        text = ""
        offset = None
        length = None
        for msg in messages:
            if offset is not None:
                break
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        text = msg.text or msg.caption
                        offset = entity.offset
                        length = entity.length
                        break
            elif msg.caption_entities:
                for entity in msg.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset is None:
            return None
        return text[offset: offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None) -> Tuple[str, str, int, str, str]:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        search_result = (await results.next())["result"][0]
        title = search_result["title"]
        duration_str = search_result["duration"]
        thumbnail = search_result["thumbnails"][0]["url"].split("?")[0]
        vidid = search_result["id"]
        duration_sec = int(time_to_seconds(duration_str)) if duration_str else 0
        return title, duration_str, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        return (await results.next())["result"][0]["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        return (await results.next())["result"][0]["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        return (await results.next())["result"][0]["thumbnails"][0]["url"].split("?")[0]

    async def video(self, link: str, videoid: Union[bool, str] = None) -> Tuple[int, str]:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        def get_video_url():
            info = extract_video_info(link)
            for fmt in info.get("formats", []):
                if fmt.get("format_id") and fmt.get("url"):
                    if fmt.get("height", 0) <= 720 and fmt.get("width", 0) <= 1280:
                        return 1, fmt["url"]
            return 0, "No suitable format found."

        return await asyncio.to_thread(get_video_url)

    async def playlist(self, link: str, limit: int, user_id, videoid: Union[bool, str] = None) -> list:
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]

        def get_playlist_ids():
            ytdl_opts = {"quiet": True, "cookiefile": cookie_txt_file()}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
            return [entry["id"] for entry in info.get("entries", [])][:limit]

        return await asyncio.to_thread(get_playlist_ids)

    async def track(self, link: str, videoid: Union[bool, str] = None) -> Tuple[dict, str]:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        search_result = (await results.next())["result"][0]
        track_details = {
            "title": search_result["title"],
            "link": search_result["link"],
            "vidid": search_result["id"],
            "duration_min": search_result["duration"],
            "thumb": search_result["thumbnails"][0]["url"].split("?")[0],
        }
        return track_details, search_result["id"]

    async def formats(self, link: str, videoid: Union[bool, str] = None) -> Tuple[list, str]:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        def get_formats():
            info = extract_video_info(link)
            available = []
            for fmt in info.get("formats", []):
                if "dash" in fmt.get("format", "").lower():
                    continue
                try:
                    _ = fmt["filesize"]
                    _ = fmt["format_id"]
                    _ = fmt["ext"]
                    _ = fmt["format_note"]
                    available.append({
                        "format": fmt["format"],
                        "filesize": fmt["filesize"],
                        "format_id": fmt["format_id"],
                        "ext": fmt["ext"],
                        "format_note": fmt["format_note"],
                        "yturl": link,
                    })
                except Exception:
                    continue
            return available

        formats_available = await asyncio.to_thread(get_formats)
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None) -> Tuple[str, str, str, str]:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=10)
        entries = (await results.next()).get("result")
        selected = entries[query_type]
        return selected["title"], selected["duration"], selected["thumbnails"][0]["url"].split("?")[0], selected["id"]

    async def download(self, link: str, mystic, video: Union[bool, str] = None,
                       videoid: Union[bool, str] = None,
                       songaudio: Union[bool, str] = None,
                       songvideo: Union[bool, str] = None,
                       format_id: Union[bool, str] = None,
                       title: Union[bool, str] = None) -> Union[Tuple[str, bool], None]:
        if videoid:
            vid_id = link
            link = self.base + link

        loop = asyncio.get_running_loop()
        
        def video_dl():
            ydl_opts = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile": cookie_txt_file(),
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
            out_path = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(out_path):
                return out_path
            ydl.download([link])
            return out_path

        def song_video_dl():
            formats_opt = f"{format_id}+140"
            fpath = f"downloads/{title}"
            ydl_opts = {
                "format": formats_opt,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie_txt_file(),
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

        def song_audio_dl():
            fpath = f"downloads/{title}.%(ext)s"
            ydl_opts = {
                "format": format_id,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie_txt_file(),
                "prefer_ffmpeg": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

        if songvideo:
            query = title
            song_data = await fetch_song(query, "video")
            if song_data and "link" in song_data and not song_data.get("error"):
                return song_data["link"], True
            await loop.run_in_executor(None, song_video_dl)
            return f"downloads/{title}.mp4", False
        elif songaudio:
            query = title
            song_data = await fetch_song(query, "audio")
            if song_data and "link" in song_data and not song_data.get("error"):
                return song_data["link"], True
            await loop.run_in_executor(None, song_audio_dl)
            return f"downloads/{title}.mp3", False
        elif video:
            query = await self.title(link, videoid)
            song_data = await fetch_song(query, "video")
            if song_data and "link" in song_data and not song_data.get("error"):
                return song_data["link"], True
            else:
                if await is_on_off(1):
                    downloaded_file = await loop.run_in_executor(None, video_dl)
                    direct = True
                else:
                    downloaded_file = await loop.run_in_executor(None, video_dl)
                    direct = True
        else:
            query = await self.title(link, videoid)
            song_data = await fetch_song(query, "audio")
            if song_data and "link" in song_data and not song_data.get("error"):
                return song_data["link"], True
            else:
                # Fallback to yt-dlp for audio download
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": "downloads/%(id)s.%(ext)s",
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "cookiefile": cookie_txt_file(),
                    "no_warnings": True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(link, download=False)
                return info.get('url'), True

        return downloaded_file, direct
