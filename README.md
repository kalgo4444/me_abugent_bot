# me_telegram_bot

A small Telegram bot that shows you your Telegram account data: ID, name, username,
Premium status, bio, birthdate, emoji status, accent color, profile photo count and more.
It can also identify the current chat, the original sender of a forwarded message, and
users, groups or channels you share with it.

No database and no webhooks. It uses long polling, stores nothing, and logs only user IDs.

## Features

| Command / action | Returns |
|---|---|
| `/start` | Greeting and the main keyboard (`👤 My info`, `💬 Chat info`, `👥 Share a user`) |
| `/me` or `👤 My info` | Your account card, attached to your current profile photo |
| `/chat` or `💬 Chat info` | Chat ID, type, title, username, message ID, topic thread ID (works in groups) |
| `👥 Share a user` | Buttons to pick up to 10 users, a group or a channel, then shows their IDs and details |
| Forward a message | Original sender: user card, hidden-user name, or chat/channel ID, title, username |
| `/help` | List of commands |

### Example `/me` output

```
👤 Your Telegram info

🆔 ID: 123456789
👤 First name: Abdulaziz
👤 Last name: Abdugafurov
👤 Full name: Abdulaziz Abdugafurov
🔗 Username: @example
⭐ Premium: ✅ Yes
🤖 Bot: ❌ No
🌐 Language: uz
📎 Attachment menu: ❌ No
📝 Bio: Full-stack developer
🎂 Birthdate: —
😀 Emoji status: —
🎨 Accent color: 3
🖼 Profile photos: 4
🔗 Link: https://t.me/example
```

The ID is shown in monospace, so you can tap it to copy. Missing fields show as `—`.

## 1. Get a bot token

1. Open [@BotFather](https://t.me/BotFather) in Telegram.
2. Send `/newbot` and follow the prompts.
3. Copy the token it gives you (looks like `123456789:AA...`).

## 2. Run with Docker (recommended)

```bash
cp .env.example .env          # then set BOT_TOKEN in .env
docker compose up -d --build
```

| Task | Command |
|---|---|
| Follow logs | `docker compose logs -f` |
| Stop | `docker compose down` |
| Rebuild after code changes | `docker compose up -d --build` |

The container runs as a non-root user, restarts automatically (`restart: unless-stopped`),
and rotates logs (3 × 10 MB).

## 3. Run locally without Docker

Requires Python 3.14.

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then set BOT_TOKEN in .env
python -m bot.main
```

A local `.env` file is read automatically. Variables already set in your environment take
precedence.

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | yes | — | Token from @BotFather. The bot exits with a clear error if it is missing. |
| `LOG_LEVEL` | no | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL` |

## Project structure

```
bot/
├── main.py            # builds the Application, registers handlers, runs polling
├── config.py          # loads BOT_TOKEN / LOG_LEVEL
├── keyboards.py       # reply keyboards and button labels
├── formatters.py      # HTML cards; every user value is escaped here
└── handlers/
    ├── start.py       # /start, /help, Back button
    ├── me.py          # /me and the shared user-card helper
    ├── chat.py        # /chat
    ├── forward.py     # forwarded messages
    └── shared.py      # Share buttons, users_shared / chat_shared
```

## Notes

- **Bio, birthdate, emoji status, accent color** come from `getChat`. If Telegram refuses
  the call (for example, for a forwarded user who never started the bot), the card still
  shows the basic fields and `—` for the rest.
- **Birthdate** appears only if the user made it visible in their privacy settings.
- **Share buttons** work only in private chats. That is a Telegram limitation.
- **In groups** the bot uses commands only (`/me`, `/chat`). With BotFather's default
  privacy mode, the bot doesn't see ordinary group messages.
