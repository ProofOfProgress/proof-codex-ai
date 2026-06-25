from unittest.mock import MagicMock, patch

from shorts_bot.invideo.mcp_client import InVideoMcpClient, _parse_sse_payloads, probe_mcp


def test_parse_sse_payloads():
    raw = 'event: message\ndata: {"jsonrpc":"2.0","id":1,"result":{"ok":true}}\n\n'
    events = _parse_sse_payloads(raw)
    assert events[0]["result"]["ok"] is True


def test_mcp_generate_video_url():
    init_body = (
        'event: message\n'
        'data: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05"}}\n\n'
    )
    gen_body = (
        'event: message\n'
        'data: {"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text",'
        '"text":"https://ai.invideo.io/ai-mcp-video?video=test-abc"}]}}\n\n'
    )

    def fake_post(url, **kwargs):
        payload = kwargs.get("json") or {}
        resp = MagicMock()
        resp.status_code = 200
        if payload.get("method") == "initialize":
            resp.headers = {"mcp-session-id": "sess123"}
            resp.text = init_body
        elif payload.get("method") == "tools/call":
            resp.headers = {}
            resp.text = gen_body
        else:
            resp.headers = {}
            resp.text = init_body
        return resp

    with patch("shorts_bot.invideo.mcp_client.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.post.side_effect = fake_post
        client = InVideoMcpClient()
        url = client.generate_video_from_script(
            script="ChatGPT Plus — Pay or Skip?",
            topic="ChatGPT Plus",
            vibe="professional",
            target_audience="AI curious adults",
            platform="youtube",
        )
    assert "ai.invideo.io" in url
    assert "test-abc" in url


def test_probe_mcp_ok():
    with patch("shorts_bot.invideo.mcp_client.InVideoMcpClient") as cls:
        cls.return_value.list_tools.return_value = [{"name": "generate-video-from-script"}]
        ok, detail = probe_mcp()
    assert ok is True
    assert "generate-video-from-script" in detail
