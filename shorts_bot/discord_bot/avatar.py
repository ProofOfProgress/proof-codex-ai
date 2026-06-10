"""Set Discord bot profile picture."""

from __future__ import annotations

import logging
from pathlib import Path

import discord

from shorts_bot.config import settings

log = logging.getLogger(__name__)

DEFAULT_AVATAR_PATH = Path("channel/brand/assets/discord_bot_avatar.png")


def _avatar_bytes(path: Path) -> bytes:
    """Square-crop and resize for Discord (512×512 PNG)."""
    from io import BytesIO

    from PIL import Image

    img = Image.open(path).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    if side != 512:
        img = img.resize((512, 512), Image.Resampling.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def resolve_avatar_path(path: Path | str | None = None) -> Path:
    p = Path(path) if path else Path(settings.discord_avatar_path or DEFAULT_AVATAR_PATH)
    if not p.is_absolute():
        p = Path.cwd() / p
    if not p.exists():
        raise FileNotFoundError(f"Discord avatar image not found: {p}")
    return p


async def set_bot_avatar(
    bot: discord.Client,
    *,
    path: Path | str | None = None,
) -> str:
    """Update bot user avatar (requires bot token)."""
    if bot.user is None:
        raise RuntimeError("Bot user not ready — call after on_ready.")

    avatar_path = resolve_avatar_path(path)
    data = _avatar_bytes(avatar_path)
    if len(data) > 8 * 1024 * 1024:
        raise ValueError("Discord avatar must be under 8MB.")

    await bot.user.edit(avatar=data)
    msg = f"Discord avatar updated from {avatar_path.name}"
    log.info(msg)
    return msg


def set_bot_avatar_sync(*, path: Path | str | None = None) -> str:
    """One-shot avatar update without running the full bot loop."""

    if not settings.has_discord:
        raise RuntimeError("DISCORD_BOT_TOKEN missing in .env")

    avatar_path = resolve_avatar_path(path)

    class _Once(discord.Client):
        async def on_ready(self) -> None:
            try:
                result = await set_bot_avatar(self, path=avatar_path)
                print(result)
            finally:
                await self.close()

    intents = discord.Intents.default()
    client = _Once(intents=intents)
    client.run(settings.discord_bot_token, log_handler=None)
    return f"Avatar set from {avatar_path.name}"
