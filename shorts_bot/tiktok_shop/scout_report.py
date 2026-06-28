"""Human-readable scout summaries for agents and owner."""

from __future__ import annotations

from shorts_bot.tiktok_shop.kalodata_rules import PRODUCT_CHECKS


def format_scout_report(products: list[dict], *, preset: str) -> str:
    if not products:
        return f"No products saved for preset={preset!r}. Pick in FastMoss app or run scout when API ships."

    lines = [f"Product research ({preset}) — {len(products)} picks in data/tiktok_shop/products.json", ""]
    for i, row in enumerate(products, 1):
        name = str(row.get("product_name") or "")[:60]
        pid = row.get("product_id", "")
        score = float(row.get("score") or 0)
        comm = float(row.get("commission_usd") or 0)
        rate = float(row.get("commission_rate") or 0)
        price = float(row.get("price") or 0)
        gmv = int(float(row.get("gmv_period") or 0))
        creators = row.get("creators", "")
        videos = row.get("videos", "")
        lines.append(
            f"{i}. {name}  [score {score:.0f}]  id={pid}\n"
            f"   ${comm}/sale ({rate * 100:.0f}% of ${price:.0f})  "
            f"GMV ${gmv:,}  creators={creators}  videos={videos}"
        )
        cover = str(row.get("cover_url") or "")
        if cover:
            lines.append(f"   cover: {cover[:80]}...")
        lines.append("")

    lines.append("Confirm in FastMoss before you commit (course Module 3):")
    for check in PRODUCT_CHECKS:
        lines.append(f"- {check}")
    return "\n".join(lines)
