# Plan me_abugent_bot

## Role
You are a senior Python developer. Build a simple, production-ready Telegram bot named **`me_telegram_bot`** that shows a user their Telegram account information.
 
## Stack
- **Python 3.14** (`python:3.14-slim` Docker image)
- **python-telegram-bot** `>=22.8,<23` (async API, `Application` + handlers)
- **Docker** + **Docker Compose**
- Config through `.env` (no hardcoded token)
- Long polling (no webhook, no database)
## Goal
When a user interacts with the bot, it replies with a clean, formatted card of their Telegram data: ID, name, username, Premium status, and other available fields.
 
---
 
## Features
 
### 1. `/start`
- Greets the user by first name.
- Short explanation of what the bot does.
- Shows a reply keyboard with buttons: `👤 My info`, `💬 Chat info`, `👥 Share a user`.
### 2. `/me` (and `👤 My info` button)
Reply with the user's data from `update.effective_user` + `bot.get_chat(user_id)` (`ChatFullInfo`):
 
| Field | Source |
|---|---|
| ID | `user.id` |
| First name | `user.first_name` |
| Last name | `user.last_name` |
| Full name | `user.full_name` |
| Username | `user.username` (as `@username` or "—") |
| Profile link | `user.link` / `tg://user?id=<id>` |
| Premium | `user.is_premium` (✅ / ❌) |
| Is bot | `user.is_bot` |
| Language code | `user.language_code` |
| Added to attachment menu | `user.added_to_attachment_menu` |
| Bio | `chat_full_info.bio` |
| Birthdate | `chat_full_info.birthdate` (if shared) |
| Emoji status | `chat_full_info.emoji_status_custom_emoji_id` |
| Accent color | `chat_full_info.accent_color_id` |
| Profile photos count | `bot.get_user_profile_photos(user_id, limit=1).total_count` |
 
- Send the user's current profile photo (if any) with the info as caption.
- Show `ID` in `<code>` tags so it is tap-to-copy.
- Missing/None fields display as `—`.
### 3. `/chat` (and `💬 Chat info` button)
Show current chat data: `chat.id`, `chat.type`, `chat.title`, `chat.username`, `message.message_id`, `message.message_thread_id` (topics). Works in private chats and groups.
 
### 4. Forwarded message lookup
- If the user forwards a message, read `message.forward_origin`:
  - `MessageOriginUser` → show the original sender's info.
  - `MessageOriginHiddenUser` → show `sender_user_name` + note "user hid their account".
  - `MessageOriginChat` / `MessageOriginChannel` → show chat/channel ID, title, username.
### 5. Share a user / chat (`👥 Share a user` button)
- Use `KeyboardButtonRequestUsers` (request name, username, photo) and `KeyboardButtonRequestChat`.
- Handle `message.users_shared` / `message.chat_shared` and reply with the shared IDs and fields.
### 6. `/help`
List all commands and what each returns.
 
### 7. Bot commands menu
Register commands on startup with `bot.set_my_commands` in `post_init`: `start`, `me`, `chat`, `help`.
 
---
 
## Project Structure
```
me_telegram_bot/
├── bot/
│   ├── __init__.py
│   ├── main.py            # build Application, register handlers, run_polling
│   ├── config.py          # load env vars (BOT_TOKEN, LOG_LEVEL)
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py       # /start, /help
│   │   ├── me.py          # /me
│   │   ├── chat.py        # /chat
│   │   ├── forward.py     # forwarded messages
│   │   └── shared.py      # users_shared / chat_shared
│   ├── keyboards.py       # reply keyboards
│   └── formatters.py      # build HTML text cards, escape values
├── .env.example
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```
 
---
 
## Implementation Requirements
- Use `ParseMode.HTML`; escape all user-provided text with `html.escape`.
- Type hints on all functions; small, single-purpose handlers.
- Logging via `logging` module (level from `LOG_LEVEL`); hide `httpx` INFO logs.
- Global error handler (`application.add_error_handler`) that logs the exception and doesn't crash the bot.
- Wrap `get_chat` / `get_user_profile_photos` in `try/except TelegramError` — fall back to basic fields.
- `drop_pending_updates=True` and `allowed_updates=Update.ALL_TYPES` in `run_polling`.
- No database, no user data stored or logged beyond user ID.
## Config
`.env.example`
```
BOT_TOKEN=your_bot_token_from_BotFather
LOG_LEVEL=INFO
```
- App fails fast with a clear error if `BOT_TOKEN` is missing.
## Docker
**Dockerfile**
- Base: `python:3.14-slim`
- `ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1`
- Install deps from `requirements.txt` with `--no-cache-dir` (separate layer for caching)
- Run as non-root user
- `CMD ["python", "-m", "bot.main"]`
**docker-compose.yml**
- Service: `me_telegram_bot`
- `build: .`, `container_name: me_telegram_bot`
- `env_file: .env`
- `restart: unless-stopped`
- Log rotation: `json-file`, `max-size: 10m`, `max-file: 3`
## README
- What the bot does + example output
- Get token from @BotFather
- Run: `cp .env.example .env` → set token → `docker compose up -d --build`
- Logs: `docker compose logs -f`
- Stop: `docker compose down`
- Local run without Docker: `python -m venv .venv`, `pip install -r requirements.txt`, `python -m bot.main`
---
 
## Example `/me` Output
```
👤 Your Telegram info
 
🆔 ID: 123456789
👤 Name: Abdulaziz Abdugafurov
🔗 Username: @example
⭐ Premium: ✅ Yes
🤖 Bot: ❌ No
🌐 Language: uz
📝 Bio: Full-stack developer
🎂 Birthdate: —
🖼 Profile photos: 4
🔗 Link: tg://user?id=123456789
```
 
---
 
## Acceptance Criteria
- [ ] `docker compose up -d --build` starts the bot with no errors
- [ ] `/start`, `/me`, `/chat`, `/help` work in private chat
- [ ] `/chat` works in a group
- [ ] Premium status shows correctly for Premium and non-Premium accounts
- [ ] Users without username / last name / photo get `—`, no crash
- [ ] Forwarded messages (visible and hidden senders) return correct info
- [ ] Shared user / chat buttons return IDs
- [ ] Special characters in names (`<`, `&`) render correctly
- [ ] Container restarts automatically after crash/reboot
## Out of Scope
Database, admin panel, webhooks, multi-language UI, analytics.
 
## Deliverable
Return all files with full contents, in the structure above, ready to run.
 