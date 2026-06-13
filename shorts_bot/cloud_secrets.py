"""Inspect which Cursor Cloud Agent secrets are configured vs injected on this VM."""

from __future__ import annotations

import os

# Must match scripts/sync_secrets.py SYNC_VARS names exactly.
YOUTUBE_SECRET_NAMES = (
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "YOUTUBE_TOKEN_JSON",
)


def _parse_names(env_key: str) -> set[str]:
    raw = os.environ.get(env_key, "")
    return {n.strip() for n in raw.split(",") if n.strip()}


def cloud_secret_lists() -> dict[str, set[str]]:
    return {
        "all": _parse_names("CLOUD_AGENT_ALL_SECRET_NAMES"),
        "injected": _parse_names("CLOUD_AGENT_INJECTED_SECRET_NAMES"),
    }


def cloud_secrets_available() -> bool:
    return bool(_parse_names("CLOUD_AGENT_ALL_SECRET_NAMES"))


def youtube_secrets_audit() -> dict[str, str]:
    """
    Per-key status for YouTube OAuth secrets.
    Values: configured | missing | configured_not_injected | present_in_env
    """
    lists = cloud_secret_lists()
    all_names = lists["all"]
    injected = lists["injected"]
    audit: dict[str, str] = {}

    for name in YOUTUBE_SECRET_NAMES:
        if os.environ.get(name):
            audit[name] = "present_in_env"
        elif name in injected:
            audit[name] = "configured"
        elif name in all_names:
            audit[name] = "configured_not_injected"
        elif cloud_secrets_available():
            audit[name] = "missing"
        else:
            audit[name] = "unknown"

    return audit


def youtube_secrets_message() -> str | None:
    """Plain-English hint when Cloud Agent metadata shows Google keys absent."""
    if not cloud_secrets_available():
        return None

    audit = youtube_secrets_audit()
    if audit.get("YOUTUBE_TOKEN_JSON") == "present_in_env":
        return None

    missing = [k for k, v in audit.items() if v == "missing"]
    not_injected = [k for k, v in audit.items() if v == "configured_not_injected"]

    if missing:
        names = ", ".join(missing)
        all_configured = sorted(cloud_secret_lists()["all"])
        sample = ", ".join(all_configured[:6])
        extra = f" (this agent has: {sample}, …)" if all_configured else ""
        return (
            f"Cursor is NOT sending {names} to this cloud VM{extra}. "
            "Cloud Agent → Secrets → add those exact names (spelling matters) → start a new agent run."
        )

    if not_injected:
        return (
            f"{', '.join(not_injected)} listed for this agent but empty on VM — "
            "re-save the secret values in Cloud Agent → Secrets."
        )

    env_google = audit.get("GOOGLE_CLIENT_ID") == "present_in_env" and audit.get(
        "GOOGLE_CLIENT_SECRET"
    ) == "present_in_env"
    if env_google:
        return None

    if all(audit.get(k) == "missing" for k in ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET")):
        return (
            "GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET not in this agent's secret list — "
            "add them in Cloud Agent → Secrets, or paste YOUTUBE_TOKEN_JSON from home PC."
        )
    return None


if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table

    console = Console()
    lists = cloud_secret_lists()
    audit = youtube_secrets_audit()

    console.print("[bold]Cursor Cloud Agent secrets (this VM)[/bold]\n")
    if not lists["all"]:
        console.print("[dim]CLOUD_AGENT_ALL_SECRET_NAMES not set — not a Cloud Agent VM[/dim]")
    else:
        table = Table("Secret", "In agent list", "Injected", "On VM")
        for name in sorted(lists["all"] | set(YOUTUBE_SECRET_NAMES)):
            in_list = "yes" if name in lists["all"] else "no"
            injected = "yes" if name in lists["injected"] else "no"
            on_vm = "yes" if os.environ.get(name) else "—"
            table.add_row(name, in_list, injected, on_vm)
        console.print(table)

    msg = youtube_secrets_message()
    if msg:
        console.print(f"\n[yellow]{msg}[/yellow]")
    elif audit.get("GOOGLE_CLIENT_ID") == "present_in_env":
        console.print("\n[green]Google OAuth secrets present on VM[/green]")
