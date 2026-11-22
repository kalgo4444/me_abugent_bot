"""Reply keyboards and their button labels."""

from telegram import (
    KeyboardButton,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUsers,
    ReplyKeyboardMarkup,
)

BTN_MY_INFO = "👤 My info"
BTN_CHAT_INFO = "💬 Chat info"
BTN_SHARE = "👥 Share a user"
BTN_BACK = "⬅️ Back"

BTN_PICK_USERS = "👤 Pick users"
BTN_PICK_GROUP = "👥 Pick a group"
BTN_PICK_CHANNEL = "📢 Pick a channel"

# request_id values echoed back in users_shared / chat_shared
REQUEST_USERS_ID = 1
REQUEST_GROUP_ID = 2
REQUEST_CHANNEL_ID = 3

MAX_SHARED_USERS = 10


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[BTN_MY_INFO, BTN_CHAT_INFO], [BTN_SHARE]],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Choose an option or forward a message",
    )


def share_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    BTN_PICK_USERS,
                    request_users=KeyboardButtonRequestUsers(
                        request_id=REQUEST_USERS_ID,
                        max_quantity=MAX_SHARED_USERS,
                        request_name=True,
                        request_username=True,
                        request_photo=True,
                    ),
                )
            ],
            [
                KeyboardButton(
                    BTN_PICK_GROUP,
                    request_chat=KeyboardButtonRequestChat(
                        request_id=REQUEST_GROUP_ID,
                        chat_is_channel=False,
                        request_title=True,
                        request_username=True,
                        request_photo=True,
                    ),
                ),
                KeyboardButton(
                    BTN_PICK_CHANNEL,
                    request_chat=KeyboardButtonRequestChat(
                        request_id=REQUEST_CHANNEL_ID,
                        chat_is_channel=True,
                        request_title=True,
                        request_username=True,
                        request_photo=True,
                    ),
                ),
            ],
            [BTN_BACK],
        ],
        resize_keyboard=True,
        input_field_placeholder="Pick a user, group or channel",
    )
