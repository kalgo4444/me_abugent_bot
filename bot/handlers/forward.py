"""Forwarded messages — show who the message originally came from."""

import logging

from telegram import (
    MessageOriginChannel,
    MessageOriginChat,
    MessageOriginHiddenUser,
    MessageOriginUser,
    Update,
)
from telegram.ext import BaseHandler, ContextTypes, MessageHandler, filters

from bot import formatters
from bot.handlers.me import send_user_card

logger = logging.getLogger(__name__)


async def forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None or message.forward_origin is None:
        return
    origin = message.forward_origin
    logger.info(
        "Forward lookup (%s) from user_id=%s",
        origin.type,
        update.effective_user.id if update.effective_user else None,
    )

    match origin:
        case MessageOriginUser():
            await send_user_card(message, context.bot, origin.sender_user, "📨 Original sender")
        case MessageOriginHiddenUser():
            await message.reply_text(formatters.hidden_user_card(origin))
        case MessageOriginChat() | MessageOriginChannel():
            await message.reply_text(formatters.origin_chat_card(origin))
        case _:
            await message.reply_text(formatters.unknown_origin_card(origin))


def get_handlers() -> list[BaseHandler]:
    return [MessageHandler(filters.ChatType.PRIVATE & filters.FORWARDED, forwarded_message)]
