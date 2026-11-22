"""/start and /help."""

import html
import logging

from telegram import ReplyKeyboardMarkup, Update
from telegram.constants import ChatType
from telegram.ext import BaseHandler, CommandHandler, ContextTypes, MessageHandler, filters

from bot.keyboards import BTN_BACK, BTN_CHAT_INFO, BTN_MY_INFO, BTN_SHARE, main_keyboard

logger = logging.getLogger(__name__)

HELP_TEXT = (
    "<b>📖 Commands</b>\n"
    "\n"
    "/start — greeting and the main keyboard\n"
    "/me — your ID, name, username, Premium status, bio, birthdate, "
    "emoji status, accent color, profile photo count and link\n"
    "/chat — current chat ID, type, title, username, message ID and topic thread ID\n"
    "/help — this message\n"
    "\n"
    "<b>🔘 Buttons</b> (private chat)\n"
    f"{BTN_MY_INFO} — same as /me\n"
    f"{BTN_CHAT_INFO} — same as /chat\n"
    f"{BTN_SHARE} — pick users, a group or a channel and get their IDs\n"
    "\n"
    "<b>📨 Forwarding</b>\n"
    "Forward any message to me and I'll show who originally sent it: "
    "a user, a hidden user, a chat or a channel."
)


def _keyboard_for(update: Update) -> ReplyKeyboardMarkup | None:
    # The reply keyboard (and its share buttons) only makes sense in private chats.
    chat = update.effective_chat
    return main_keyboard() if chat and chat.type == ChatType.PRIVATE else None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message, user = update.effective_message, update.effective_user
    if message is None:
        return
    name = html.escape(user.first_name) if user else "there"
    logger.info("/start from user_id=%s", user.id if user else None)
    await message.reply_text(
        f"👋 Hi, <b>{name}</b>!\n\n"
        "I show the Telegram data of your account, of this chat, of forwarded "
        "messages and of users or chats you share with me.\n\n"
        "Use the buttons below or /help to see everything I can do.",
        reply_markup=_keyboard_for(update),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message:
        await update.effective_message.reply_text(HELP_TEXT, reply_markup=_keyboard_for(update))


async def back_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message:
        await update.effective_message.reply_text("🏠 Main menu", reply_markup=main_keyboard())


def get_handlers() -> list[BaseHandler]:
    return [
        CommandHandler("start", start_command),
        CommandHandler("help", help_command),
        MessageHandler(filters.ChatType.PRIVATE & filters.Text([BTN_BACK]), back_button),
    ]
