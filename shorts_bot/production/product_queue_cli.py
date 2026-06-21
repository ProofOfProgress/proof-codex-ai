"""Product queue status."""

from __future__ import annotations

from rich.console import Console

from shorts_bot.production.product_queue import load_product_queue, queue_summary

console = Console()


def main() -> None:
    q = load_product_queue()
    console.print(f"[cyan]{len(q)} products queued[/cyan]")
    console.print(queue_summary())


if __name__ == "__main__":
    main()
