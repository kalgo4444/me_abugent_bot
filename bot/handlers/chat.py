"""/chat — data about the current chat and message."""

import logging

from telegram import Update
from telegram.ext import BaseHandler, CommandHandler, ContextTypes, MessageHandler, filters

from bot import formatters
from bot.keyboards import BTN_CHAT_INFO

logger = logging.getLogger(__name__)


async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return
    logger.info(
        "/chat from user_id=%s", update.effective_user.id if update.effective_user else None
    )
    await message.reply_text(formatters.chat_card(message))


def get_handlers() -> list[BaseHandler]:
    return [
        CommandHandler("chat", chat_command),
        MessageHandler(filters.Text([BTN_CHAT_INFO]), chat_command),
    ]
