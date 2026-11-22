"""/me — the user's own account card. Also exposes helpers reused by other handlers."""

import logging
from dataclasses import dataclass

from telegram import Bot, ChatFullInfo, Message, Update, User
from telegram.constants import MessageLimit
from telegram.error import TelegramError
from telegram.ext import BaseHandler, CommandHandler, ContextTypes, MessageHandler, filters

from bot import formatters
from bot.keyboards import BTN_MY_INFO

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Profile:
    full_info: ChatFullInfo | None
    photos_count: int | None
    photo_file_id: str | None


async def fetch_profile(bot: Bot, user_id: int) -> Profile:
    """Fetch extra profile data; each call degrades to None instead of failing the card."""
    full_info: ChatFullInfo | None = None
    photos_count: int | None = None
    photo_file_id: str | None = None

    try:
        full_info = await bot.get_chat(user_id)
    except TelegramError as exc:
        logger.debug("get_chat failed for user_id=%s: %s", user_id, exc)

    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
    except TelegramError as exc:
        logger.debug("get_user_profile_photos failed for user_id=%s: %s", user_id, exc)
    else:
        photos_count = photos.total_count
        if photos.photos and photos.photos[0]:
            photo_file_id = photos.photos[0][-1].file_id  # largest size

    return Profile(full_info, photos_count, photo_file_id)


async def send_user_card(message: Message, bot: Bot, user: User, title: str) -> None:
    """Reply with the user's card, attached to their current profile photo when there is one."""
    profile = await fetch_profile(bot, user.id)
    text = formatters.user_card(user, profile.full_info, profile.photos_count, title)

    if profile.photo_file_id is None:
        await message.reply_text(text)
        return

    if len(text) <= MessageLimit.CAPTION_LENGTH:
        try:
            await message.reply_photo(profile.photo_file_id, caption=text)
            return
        except TelegramError as exc:
            logger.warning("Sending profile photo failed for user_id=%s: %s", user.id, exc)
    else:
        # Rare: heavily escaped names can push the card over the caption limit.
        try:
            await message.reply_photo(profile.photo_file_id)
        except TelegramError as exc:
            logger.warning("Sending profile photo failed for user_id=%s: %s", user.id, exc)
    await message.reply_text(text)


async def me_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message, user = update.effective_message, update.effective_user
    if message is None or user is None:
        return
    logger.info("/me from user_id=%s", user.id)
    await send_user_card(message, context.bot, user, "👤 Your Telegram info")


def get_handlers() -> list[BaseHandler]:
    return [
        CommandHandler("me", me_command),
        MessageHandler(filters.ChatType.PRIVATE & filters.Text([BTN_MY_INFO]), me_command),
    ]
