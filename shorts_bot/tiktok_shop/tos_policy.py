"""
TikTok Shop Content Policy checks — zero-strike prevention (seller university 2026-03-16).

Blocks risky promotional text and vision flags before upload. Appeals are not the strategy.

Source: https://seller-sg.tiktok.com/university/essay?knowledge_id=7651420422014721&identity=1

Layered on Module 1 (course visuals) + Module 7 (misinformation words).
"""

from __future__ import annotations

import re

TOS_POLICY_URL = (
    "https://seller-sg.tiktok.com/university/essay?knowledge_id=7651420422014721&identity=1"
)
TOS_POLICY_DATE = "2026-03-16"

# --- Caption / on-screen text: exact phrase hits (lowercase match) ---

# Module 7 misinformation + TikTok misleading / price manipulation
MISINFORMATION_PHRASES: tuple[str, ...] = (
    "sale",
    "price",
    "discount",
    "coupon",
    "free shipping",
    "flash sale",
    "triple discount",
    "double discount",
    "coupon glitch",
    "limited time only",
    "lowest price",
    "best price",
    "price drop",
    "on sale now",
    "clearance sale",
    "% off",
    "percent off",
    "half off",
    "buy one get one",
    "bogo",
)

# Giveaways & purchase-based incentives (prohibited unless official tools)
GIVEAWAY_PHRASES: tuple[str, ...] = (
    "giveaway",
    "free gift",
    "spin the wheel",
    "spin to win",
    "lucky draw",
    "lucky scoop",
    "raffle",
    "sweepstakes",
    "lottery",
    "buy to win",
    "purchase to enter",
    "comment to win",
    "follow to win",
    "like to win",
    "tag to win",
    "share to win",
)

# Redirecting user traffic off-platform
REDIRECT_PHRASES: tuple[str, ...] = (
    "link in bio",
    "link in my bio",
    "dm me",
    "message me",
    "whatsapp",
    "telegram",
    "instagram",
    "facebook",
    "scan qr",
    "qr code",
    "click the link",
    "visit my website",
    "check my store",
)

# Gambling / chance-based gamification
GAMBLING_PHRASES: tuple[str, ...] = (
    "roulette",
    "jackpot",
    "place your bet",
    "place a bet",
    "casino",
    "roll the dice",
    "wheel spin",
)

# Misleading / exaggerated claims (health, beauty, results)
EXAGGERATED_CLAIM_PHRASES: tuple[str, ...] = (
    "guaranteed results",
    "100% guaranteed",
    "miracle cure",
    "instant cure",
    "doctor recommended",
    "fda approved",
    "clinically proven",
    "lose weight fast",
    "burn fat fast",
    "melt fat",
    "weight loss guaranteed",
    "cures ",
    " cure ",
)

# Weight management — product alone driving loss/gain (TikTok Shop policy)
WEIGHT_MANAGEMENT_PHRASES: tuple[str, ...] = (
    "lose weight",
    "weight loss",
    "burn fat",
    "fat burner",
    "slim down",
    "drop pounds",
)

# Auction / bidding (prohibited)
AUCTION_PHRASES: tuple[str, ...] = (
    "place a bid",
    "highest bid",
    "auction ends",
    "bid now",
    "going once",
)

# Artificial engagement
ARTIFICIAL_ENGAGEMENT_PHRASES: tuple[str, ...] = (
    "follow for follow",
    "f4f",
    "sub for sub",
    "buy followers",
    "buy likes",
)

# Political (prohibited in shop content)
POLITICAL_PHRASES: tuple[str, ...] = (
    "vote for",
    "election",
    "president ",
    "congress",
    "democrat",
    "republican",
)

PHRASE_CATEGORIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("TOS Misinformation/Price", MISINFORMATION_PHRASES),
    ("TOS Giveaways/Incentives", GIVEAWAY_PHRASES),
    ("TOS Redirect off-platform", REDIRECT_PHRASES),
    ("TOS Gambling/Chance", GAMBLING_PHRASES),
    ("TOS Exaggerated claims", EXAGGERATED_CLAIM_PHRASES),
    ("TOS Weight management", WEIGHT_MANAGEMENT_PHRASES),
    ("TOS Auction/Bidding", AUCTION_PHRASES),
    ("TOS Artificial engagement", ARTIFICIAL_ENGAGEMENT_PHRASES),
    ("TOS Political content", POLITICAL_PHRASES),
)

# Regex patterns — structural violations
REDIRECT_REGEX: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"https?://", re.I), "TOS Redirect: URL in promotional text"),
    (re.compile(r"\bwww\.\S+", re.I), "TOS Redirect: URL in promotional text"),
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "TOS Redirect: email address"),
    (re.compile(r"@\w{2,}"), "TOS Redirect: @ social handle"),
    (
        re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        "TOS Redirect: phone number in content",
    ),
    (re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"), "TOS Redirect: phone number in content"),
    (re.compile(r"\b\d+\s*%\s*off\b", re.I), "TOS Misinformation: percentage discount claim"),
    (re.compile(r"\b\d+\s*percent\s*off\b", re.I), "TOS Misinformation: percentage discount claim"),
)

# Vision QC — TikTok Shop Content Policy (in addition to Module 1 course list)
TOS_VISION_VIOLATIONS: tuple[str, ...] = (
    "Content does not clearly promote the listed product (irrelevant promotional content)",
    "Non-interactive or mostly static scene with no meaningful motion (non-interactive low-quality)",
    "Unoriginal or reposted footage — no new creative edit",
    "Misleading or false product claims visible in frame text",
    "Exaggerated health or beauty claims on packaging or overlay text",
    "Weight management claim that product alone causes loss/gain",
    "Sexually suggestive behavior or language in promotion",
    "Minors under 18 promoting product without adult present",
    "Content directed to minors to purchase",
    "Gambling, spin-wheel, lottery, or chance-based promotion visible",
    "Giveaway or purchase-based incentive messaging visible",
    "Redirect off-platform: URL, QR code, phone, email, or social handle visible",
    "Auction or bidding language visible",
    "Political references, campaign materials, or politicized issues",
    "Sensational, shocking, violent, or discriminatory imagery",
    "Fictitious or joke listing vibe (impossible/meme product not real)",
    "Intellectual property infringement — unlicensed brand/logo/personality",
    "AI-generated content that misleads, deceives, or impersonates a real person/brand",
    "Prohibited or restricted product category visible",
    "Infant or follow-on formula milk promotion",
    "Tobacco, drugs, weapons, or prescription medication visible",
)

TOS_VISION_PROMPT = (
    "TikTok Shop Content Policy (2026-03-16) — ZERO TOLERANCE in any frame:\n"
    + "\n".join(f"- {v}" for v in TOS_VISION_VIOLATIONS)
    + "\n\nAffiliate AI clips MUST: clearly show the real shoppable product, use arc camera motion "
    "(not static slideshow feel), avoid misleading price/sale text, avoid off-platform redirects, "
    "avoid giveaway/gambling cues. AIGC is allowed when not misleading — do not impersonate real people."
)


def _phrase_in_text(phrase: str, lower: str, original: str) -> bool:
    """Match phrases; use word boundaries for short tokens to avoid false positives."""
    p = phrase.strip().lower()
    if not p:
        return False
    if p in ("% off", "percent off") or "%" in p:
        return p in lower
    if len(p) <= 5 and " " not in p:
        return bool(re.search(rf"\b{re.escape(p)}\b", lower))
    return p in lower


def check_promotional_text(text: str, *, field: str = "caption") -> list[str]:
    """Return TOS violations found in caption, title, or description."""
    if not (text or "").strip():
        return []
    lower = text.lower()
    hits: list[str] = []

    for category, phrases in PHRASE_CATEGORIES:
        for phrase in phrases:
            if _phrase_in_text(phrase, lower, text):
                hits.append(f"{category}: {field} contains '{phrase.strip()}'")

    for pattern, message in REDIRECT_REGEX:
        if pattern.search(text):
            hits.append(f"{message} ({field})")

    # Deduplicate
    seen: set[str] = set()
    unique: list[str] = []
    for h in hits:
        key = h.lower()
        if key not in seen:
            seen.add(key)
            unique.append(h)
    return unique


def merge_banned_caption_phrases() -> tuple[str, ...]:
    """All static phrase bans for module1_qc backward compatibility."""
    out: list[str] = []
    for _cat, phrases in PHRASE_CATEGORIES:
        out.extend(phrases)
    return tuple(dict.fromkeys(out))
