"""Entry point: build the Application, register handlers and start long polling."""

import logging
import sys

from telegram import BotCommand, LinkPreviewOptions, Update
from telegram.constants import ParseMode
from telegram.ext import Application, ApplicationBuilder, ContextTypes, Defaults

from bot.config import Config, ConfigError, load_config
from bot.handlers import get_handlers

logger = logging.getLogger("bot")

BOT_COMMANDS = [
    BotCommand("start", "Start the bot and show the menu"),
    BotCommand("me", "Show your Telegram account info"),
    BotCommand("chat", "Show info about the current chat"),
    BotCommand("help", "List commands and what they return"),
]


def setup_logging(level: int) -> None:
    logging.basicConfig(
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        level=level,
    )
    # httpx logs every request (including the token in the URL) at INFO.
    logging.getLogger("httpx").setLevel(logging.WARNING)


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(BOT_COMMANDS)
    me = await application.bot.get_me()
    logger.info("Bot @%s started (id=%s)", me.username, me.id)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = (
        update.effective_user.id
        if isinstance(update, Update) and update.effective_user
        else None
    )
    logger.error("Unhandled error (user_id=%s)", user_id, exc_info=context.error)


def build_application(config: Config) -> Application:
    application = (
        ApplicationBuilder()
        .token(config.bot_token)
        .defaults(
            Defaults(
                parse_mode=ParseMode.HTML,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )
        )
        .post_init(post_init)
        .build()
    )
    application.add_handlers(get_handlers())
    application.add_error_handler(error_handler)
    return application


def main() -> None:
    try:
        config = load_config()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    setup_logging(config.log_level)
    application = build_application(config)
    logger.info("Starting long polling")
    application.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
