from unittest.mock import MagicMock, patch

from shorts_bot.browser.session import BrowseResult, resolve_url
from shorts_bot.services.chat_router import parse_browse_request


def test_resolve_url_aliases():
    assert "vidiq.com" in resolve_url("vidiq")
    assert "studio.youtube.com" in resolve_url("youtube")
    assert resolve_url("https://example.com") == "https://example.com"


def test_parse_browse_commands():
    assert parse_browse_request("browse vidiq") == ("vidiq", False)
    assert parse_browse_request("browser open trends") == ("trends", True)
    assert parse_browse_request("browser login youtube") == ("youtube", True)
    assert parse_browse_request("browser status") == ("__status__", False)


def test_browse_web_ops(monkeypatch):
    from shorts_bot.services.ops import BotOperations

    fake = BrowseResult(url="https://vidiq.com", title="vidIQ", text="keyword data here")
    monkeypatch.setattr(
        "shorts_bot.browser.session.browse_url",
        lambda url, **kw: fake,
    )
    out = BotOperations().browse_web("vidiq")
    assert "vidIQ" in out
    assert "keyword" in out


def test_is_playwright_ready():
    from shorts_bot.browser.session import is_playwright_ready

    ok, detail = is_playwright_ready()
    assert isinstance(ok, bool)
    assert detail
