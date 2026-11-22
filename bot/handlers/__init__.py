"""Collect all update handlers in the order they must be registered."""

from telegram.ext import BaseHandler

from bot.handlers import chat, forward, me, shared, start


def get_handlers() -> list[BaseHandler]:
    # Forwards go first so a forwarded "👤 My info" text isn't treated as a button press.
    return [
        *forward.get_handlers(),
        *shared.get_handlers(),
        *start.get_handlers(),
        *me.get_handlers(),
        *chat.get_handlers(),
    ]
