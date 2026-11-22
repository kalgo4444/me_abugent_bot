"""Share a user / chat — the request keyboard and the users_shared / chat_shared replies."""

import logging

from telegram import Update
from telegram.constants import ChatType
from telegram.ext import BaseHandler, ContextTypes, MessageHandler, filters

from bot import formatters
from bot.keyboards import BTN_SHARE, REQUEST_CHANNEL_ID, main_keyboard, share_keyboard

logger = logging.getLogger(__name__)


async def share_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message, chat = update.effective_message, update.effective_chat
    if message is None or chat is None:
        return
    if chat.type != ChatType.PRIVATE:
        await message.reply_text("👥 Sharing users and chats works only in a private chat with me.")
        return
    await message.reply_text(
        "Pick what you want to share — I'll reply with its ID and details.",
        reply_markup=share_keyboard(),
    )


async def users_shared(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None or message.users_shared is None:
        return
    logger.info(
        "users_shared (%d) from user_id=%s",
        len(message.users_shared.users),
        update.effective_user.id if update.effective_user else None,
    )
    await message.reply_text(
        formatters.shared_users_card(message.users_shared), reply_markup=main_keyboard()
    )


async def chat_shared(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None or message.chat_shared is None:
        return
    kind = "channel" if message.chat_shared.request_id == REQUEST_CHANNEL_ID else "group"
    logger.info(
        "chat_shared (%s) from user_id=%s",
        kind,
        update.effective_user.id if update.effective_user else None,
    )
    await message.reply_text(
        formatters.shared_chat_card(message.chat_shared, kind), reply_markup=main_keyboard()
    )


def get_handlers() -> list[BaseHandler]:
    return [
        MessageHandler(filters.Text([BTN_SHARE]), share_button),
        MessageHandler(filters.StatusUpdate.USERS_SHARED, users_shared),
        MessageHandler(filters.StatusUpdate.CHAT_SHARED, chat_shared),
    ]
