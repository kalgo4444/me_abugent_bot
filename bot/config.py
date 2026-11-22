"""Configuration loaded from environment variables (and an optional local .env file)."""

import logging
import os
from dataclasses import dataclass
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True, slots=True)
class Config:
    bot_token: str
    log_level: int


def _load_env_file(path: Path) -> None:
    """Populate os.environ from a simple KEY=VALUE file without overriding existing vars.

    Docker Compose injects variables via ``env_file``; this only matters for local runs.
    """
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.removeprefix("export ").strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _parse_log_level(raw: str) -> int:
    name = raw.strip().upper() or "INFO"
    level = logging.getLevelNamesMapping().get(name)
    if level is None:
        raise ConfigError(
            f"LOG_LEVEL={raw!r} is invalid. Use one of: DEBUG, INFO, WARNING, ERROR, CRITICAL."
        )
    return level


def load_config() -> Config:
    """Read configuration, failing fast with a clear message if BOT_TOKEN is missing."""
    _load_env_file(ENV_FILE)

    token = os.environ.get("BOT_TOKEN", "").strip()
    if not token or token == "your_bot_token_from_BotFather":
        raise ConfigError(
            "BOT_TOKEN is not set. Copy .env.example to .env and put your token "
            "from @BotFather into it."
        )

    return Config(
        bot_token=token,
        log_level=_parse_log_level(os.environ.get("LOG_LEVEL", "INFO")),
    )
