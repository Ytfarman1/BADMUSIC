import time
import random
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from BADMUSIC import app
from BADMUSIC.misc import _boot_
from BADMUSIC.plugins.sudo.sudoers import sudoers_list
from BADMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from BADMUSIC.utils.decorators.language import LanguageStart
from BADMUSIC.utils.formatters import get_readable_time
from BADMUSIC.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

# ✨ Random Welcome Banners
IMAGE = [
    "https://graph.org/file/f76fd86d1936d45a63c64.jpg",
    "https://graph.org/file/a0893f3a1e6777f6de821.jpg",
    "https://graph.org/file/eaa3a2602e43844a488a5.jpg",
    "https://graph.org/file/52713c9fe9253ae668f13.jpg",
    "https://graph.org/file/9e23720fedc47259b6195.jpg",
]

# ✨ Fancy emoji animation
WELCOME_EMOJIS = ["🎧", "🎶", "🎵", "🎼", "🎤", "🎛️", "🎹", "🎷", "🥁", "🎺"]

async def animate_text(message: Message, text: str, delay: float = 0.08):
    """Typewriter-style animation for message text."""
    temp = ""
    for char in text:
        temp += char
        await message.edit_text(temp)
        await asyncio.sleep(delay)

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    await message.delete()

    # 🌈 Small typing animation
    emoji = random.choice(WELCOME_EMOJIS)
    temp_msg = await message.reply_text(f"{emoji} Starting...")
    await asyncio.sleep(0.7)
    await animate_text(temp_msg, f"{emoji} Booting system...")
    await asyncio.sleep(0.7)
    await animate_text(temp_msg, f"{emoji} Loading modules...")
    await asyncio.sleep(0.6)
    await temp_msg.delete()

    # If /start has arguments
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name.startswith("help"):
            keyboard = help_pannel(_)
            return await safe_reply_photo(
                message,
                random.choice(IMAGE),
                _["help_1"].format(config.SUPPORT_CHAT),
                keyboard
            )

        elif name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await safe_send_log(message, "sudo list check")
            return

        elif name.startswith("inf"):
            m = await message.reply_text("🔎 Searching...")
            query = f"https://www.youtube.com/watch?v={name.replace('info_', '', 1)}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]

            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text=_["S_B_8"], url=link)],
                    [InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT)],
                ]
            )
            await m.delete()
            await safe_reply_photo(message, thumbnail, searched_text, key)
            if await is_on_off(2):
                await safe_send_log(message, "track info check")
            return

    # Default /start message
    out = private_panel(_)
    caption = (
        f"✨ **Hey {message.from_user.mention}!**\n\n"
        f"🎧 Welcome to **{app.mention}** — your powerful Telegram Music Bot.\n"
        f"Stream high-quality audio from YouTube, Spotify & more directly in your groups!\n\n"
        f"💡 Use the menu below to explore all commands."
    )
    await safe_reply_photo(message, random.choice(IMAGE), caption, InlineKeyboardMarkup(out))

    if await is_on_off(2):
        await safe_send_log(message, "started the bot")

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    caption = (
        f"✅ **{app.mention} is Online!**\n\n"
        f"⏱ Uptime: `{get_readable_time(uptime)}`\n"
        f"🎶 Enjoy seamless high-quality streaming.\n"
    )
    await safe_reply_photo(
        message,
        random.choice(IMAGE),
        caption,
        InlineKeyboardMarkup(out)
    )
    await message.delete()
    await add_served_chat(message.chat.id)

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except Exception:
                    pass

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(app.mention, f"https://t.me/{app.username}?start=sudolist", config.SUPPORT_CHAT),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                caption = (
                    f"🎵 **Hey {message.chat.title}!**\n\n"
                    f"Thanks for adding {app.mention} here ❤️\n"
                    f"I can now play songs, streams & playlists with premium quality.\n\n"
                    f"Use `/play [song name]` to get started!"
                )
                await safe_reply_photo(
                    message,
                    random.choice(IMAGE),
                    caption,
                    InlineKeyboardMarkup(out)
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()

        except Exception as ex:
            print(f"[WELCOME ERROR] {ex}")

# 🔰 Safe photo/text fallback
async def safe_reply_photo(message, photo, caption, markup):
    try:
        await message.reply_photo(photo=photo, caption=caption, reply_markup=markup)
    except Exception as e:
        print(f"[PHOTO ERROR] {e}")
        try:
            await message.reply_text(caption, reply_markup=markup, disable_web_page_preview=True)
        except Exception as e2:
            print(f"[TEXT FALLBACK ERROR] {e2}")

# 🔰 Safe log sender
async def safe_send_log(message, reason):
    try:
        await app.send_message(
            chat_id=config.LOGGER_ID,
            text=(
                f"❖ {message.from_user.mention} {reason}.\n"
                f"<b>● User ID ➤</b> <code>{message.from_user.id}</code>\n"
                f"<b>● Username ➤</b> @{message.from_user.username or 'N/A'}"
            ),
        )
    except Exception as e:
        print(f"[LOG ERROR] {e}")
