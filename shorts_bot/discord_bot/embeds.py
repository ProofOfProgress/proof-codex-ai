from __future__ import annotations

import discord


def status_embed(data: dict, *, web_port: int) -> discord.Embed:
    from shorts_bot.config import settings

    yt = data.get("youtube", {})
    name = settings.youtube_channel_name or "Don't Blink"
    embed = discord.Embed(title=name, description="Watch the whole thing.", color=0x1A0A0A)
    chat = "offline"
    if data.get("openai"):
        provider = data.get("chat_provider", "")
        chat = f"full ({provider})" if provider else "full"
    embed.add_field(name="Chat", value=chat, inline=True)
    embed.add_field(name="YouTube", value="ready" if yt.get("ready") else "setup needed", inline=True)
    embed.add_field(name="Discord", value="on", inline=True)
    embed.add_field(name="Improvements", value=str(data.get("pending_improvements", 0)), inline=True)
    embed.add_field(name="Drafts", value=str(data.get("pending_drafts", 0)), inline=True)
    embed.add_field(name="Dev tasks", value=str(data.get("pending_dev", 0)), inline=True)
    embed.set_footer(text=f"Web UI: http://localhost:{web_port}")
    return embed


def pending_embed(improvements: list, drafts: list) -> discord.Embed:
    embed = discord.Embed(title="Pending approvals", color=0x7C5CFF)
    imp_lines = [f"#{i['id']} [{i['category']}] {i['title'][:60]}" for i in improvements[:6]] or ["(none)"]
    draft_lines = [f"#{d['id']} {d['topic'][:60]}" for d in drafts[:6]] or ["(none)"]
    embed.add_field(name="Improvements", value="\n".join(imp_lines), inline=False)
    embed.add_field(name="Drafts", value="\n".join(draft_lines), inline=False)
    embed.set_footer(text="!yes <id> or !no <id>  ·  !draftyes <id>")
    return embed
