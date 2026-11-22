"""Build HTML text cards. Every user-provided value is escaped here."""

import html
from collections.abc import Sequence
from datetime import datetime

from telegram import (
    Birthdate,
    Chat,
    ChatFullInfo,
    ChatShared,
    Message,
    MessageOrigin,
    MessageOriginChannel,
    MessageOriginChat,
    MessageOriginHiddenUser,
    SharedUser,
    User,
    UsersShared,
)

EMPTY = "—"

Row = tuple[str, str, str]  # (emoji, label, already-escaped HTML value)


# ---------------------------------------------------------------- primitives


def esc(value: object | None) -> str:
    """Escape a value for HTML, rendering None / empty as an em dash."""
    if value is None or value == "":
        return EMPTY
    return html.escape(str(value))


def code(value: object | None) -> str:
    """Tap-to-copy monospace value."""
    if value is None or value == "":
        return EMPTY
    return f"<code>{html.escape(str(value))}</code>"


def yes_no(value: bool | None) -> str:
    # Telegram omits boolean flags that are false, so None means "no".
    return "✅ Yes" if value else "❌ No"


def username(value: str | None) -> str:
    return esc(f"@{value}") if value else EMPTY


def user_link(user_id: int, name: str | None) -> str:
    return esc(f"https://t.me/{name}") if name else esc(f"tg://user?id={user_id}")


def chat_link(name: str | None) -> str:
    return esc(f"https://t.me/{name}") if name else EMPTY


def birthdate(value: Birthdate | None) -> str:
    if value is None:
        return EMPTY
    text = f"{value.day:02d}.{value.month:02d}"
    if value.year:
        text += f".{value.year}"
    return esc(text)


def timestamp(value: datetime | None) -> str:
    if value is None:
        return EMPTY
    return esc(value.strftime("%Y-%m-%d %H:%M:%S %Z").strip())


def render(title: str, rows: Sequence[Row], footer: str | None = None) -> str:
    lines = [f"<b>{html.escape(title)}</b>", ""]
    lines += [f"{emoji} <b>{html.escape(label)}:</b> {value}" for emoji, label, value in rows]
    if footer:
        lines += ["", f"<i>{html.escape(footer)}</i>"]
    return "\n".join(lines)


# ---------------------------------------------------------------- users


def user_card(
    user: User,
    full_info: ChatFullInfo | None,
    photos_count: int | None,
    title: str,
) -> str:
    """Full user card. ``full_info`` / ``photos_count`` are None when the API call failed."""
    rows: list[Row] = [
        ("🆔", "ID", code(user.id)),
        ("👤", "First name", esc(user.first_name)),
        ("👤", "Last name", esc(user.last_name)),
        ("👤", "Full name", esc(user.full_name)),
        ("🔗", "Username", username(user.username)),
        ("⭐", "Premium", yes_no(user.is_premium)),
        ("🤖", "Bot", yes_no(user.is_bot)),
        ("🌐", "Language", esc(user.language_code)),
        ("📎", "Attachment menu", yes_no(user.added_to_attachment_menu)),
        ("📝", "Bio", esc(full_info.bio if full_info else None)),
        ("🎂", "Birthdate", birthdate(full_info.birthdate if full_info else None)),
        (
            "😀",
            "Emoji status",
            code(full_info.emoji_status_custom_emoji_id if full_info else None),
        ),
        ("🎨", "Accent color", esc(full_info.accent_color_id if full_info else None)),
        ("🖼", "Profile photos", esc(photos_count)),
        ("🔗", "Link", user_link(user.id, user.username)),
    ]
    return render(title, rows)


def shared_users_card(users_shared: UsersShared) -> str:
    blocks = [
        f"<b>👥 Shared users: {len(users_shared.users)}</b>",
        f"<i>request_id: {users_shared.request_id}</i>",
    ]
    for index, shared in enumerate(users_shared.users, start=1):
        blocks += ["", f"<b>#{index}</b>", *_shared_user_lines(shared)]
    return "\n".join(blocks)


def _shared_user_lines(shared: SharedUser) -> list[str]:
    full_name = " ".join(part for part in (shared.first_name, shared.last_name) if part)
    rows: list[Row] = [
        ("🆔", "ID", code(shared.user_id)),
        ("👤", "Name", esc(full_name)),
        ("🔗", "Username", username(shared.username)),
        ("🖼", "Photo", yes_no(bool(shared.photo))),
        ("🔗", "Link", user_link(shared.user_id, shared.username)),
    ]
    return [f"{emoji} <b>{label}:</b> {value}" for emoji, label, value in rows]


# ---------------------------------------------------------------- chats


def chat_card(message: Message) -> str:
    chat = message.chat
    rows: list[Row] = [
        ("🆔", "Chat ID", code(chat.id)),
        ("🏷", "Type", esc(chat.type)),
        ("📛", "Title", esc(chat.title)),
    ]
    if chat.type == Chat.PRIVATE:
        rows.append(("👤", "Name", esc(chat.full_name)))
    rows += [
        ("🔗", "Username", username(chat.username)),
        ("🗂", "Forum", yes_no(chat.is_forum)),
        ("✉️", "Message ID", code(message.message_id)),
        ("🧵", "Thread ID", code(message.message_thread_id)),
    ]
    return render("💬 Chat info", rows)


def shared_chat_card(chat_shared: ChatShared, kind: str) -> str:
    rows: list[Row] = [
        ("🆔", "Chat ID", code(chat_shared.chat_id)),
        ("📛", "Title", esc(chat_shared.title)),
        ("🔗", "Username", username(chat_shared.username)),
        ("🖼", "Photo", yes_no(bool(chat_shared.photo))),
        ("🔗", "Link", chat_link(chat_shared.username)),
        ("🔢", "Request ID", esc(chat_shared.request_id)),
    ]
    return render(f"📤 Shared {kind}", rows)


# ---------------------------------------------------------------- forwards


def hidden_user_card(origin: MessageOriginHiddenUser) -> str:
    rows: list[Row] = [
        ("👤", "Name", esc(origin.sender_user_name)),
        ("🕒", "Sent", timestamp(origin.date)),
    ]
    return render(
        "📨 Forwarded from a hidden user",
        rows,
        footer="The user hid their account in privacy settings, so only the name is visible.",
    )


def origin_chat_card(origin: MessageOriginChat | MessageOriginChannel) -> str:
    if isinstance(origin, MessageOriginChannel):
        chat, title = origin.chat, "📨 Forwarded from a channel"
        post_link = (
            esc(f"https://t.me/{chat.username}/{origin.message_id}") if chat.username else EMPTY
        )
        extra: list[Row] = [
            ("✉️", "Message ID", code(origin.message_id)),
            ("🔗", "Post link", post_link),
        ]
    else:
        chat, title = origin.sender_chat, "📨 Forwarded from a chat"
        extra = []

    rows: list[Row] = [
        ("🆔", "Chat ID", code(chat.id)),
        ("🏷", "Type", esc(chat.type)),
        ("📛", "Title", esc(chat.title)),
        ("🔗", "Username", username(chat.username)),
        *extra,
        ("✍️", "Signature", esc(origin.author_signature)),
        ("🕒", "Sent", timestamp(origin.date)),
    ]
    return render(title, rows)


def unknown_origin_card(origin: MessageOrigin) -> str:
    return render(
        "📨 Forwarded message",
        [("🏷", "Origin type", esc(origin.type)), ("🕒", "Sent", timestamp(origin.date))],
    )
