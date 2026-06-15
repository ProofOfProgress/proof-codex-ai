from pathlib import Path
from unittest.mock import MagicMock, patch

from shorts_bot.production.vision_qc import _gemini_vision_review, _is_creature_lunge_lab


def test_is_creature_lunge_lab_from_marker(tmp_path):
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "creature_lunge_lab.json").write_text('{"creature_only": true}', encoding="utf-8")
    assert _is_creature_lunge_lab(pack) is True


def test_is_creature_lunge_lab_from_blender_spec(tmp_path):
    pack = tmp_path / "pack"
    clips = pack / "clips"
    clips.mkdir(parents=True)
    (clips / "blender_spec.json").write_text(
        '{"backend": "blender", "creature_only": true}', encoding="utf-8"
    )
    assert _is_creature_lunge_lab(pack) is True


def test_gemini_vision_review_creature_lab_prompt(tmp_path):
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "creature_lunge_lab.json").write_text('{"lab": "creature_lunge"}', encoding="utf-8")

    frames = [(2.5, pack / "f.jpg")]
    (pack / "f.jpg").write_bytes(b"\xff" * 100)

    mock_resp = MagicMock()
    mock_resp.choices = [
        MagicMock(message=MagicMock(content='{"score":8,"pass":true,"issues":[],"warnings":[]}'))
    ]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_resp
    mock_backend = MagicMock(client=mock_client, model="gemini-2.5-flash-lite", provider="gemini")

    with patch("shorts_bot.llm.provider.get_llm_backend", return_value=mock_backend):
        _gemini_vision_review(
            frames,
            topic="creature lunge",
            hook="face fill",
            pack_dir=pack,
        )

    prompt = mock_client.chat.completions.create.call_args.kwargs["messages"][0]["content"][0]["text"]
    assert "CREATURE LUNGE LAB" in prompt
    assert "NOT AI video clips" in prompt
    assert "do NOT fail for missing gas station" in prompt
    assert "AI motion clips" not in prompt


def test_gemini_vision_review_includes_lights_are_off_for_blender_pack(tmp_path):
    pack = tmp_path / "pack"
    clips = pack / "clips"
    clips.mkdir(parents=True)
    (clips / "blender_spec.json").write_text('{"backend": "blender"}', encoding="utf-8")

    frames = [(0.8, pack / "f.jpg")]
    (pack / "f.jpg").write_bytes(b"\xff" * 100)

    mock_resp = MagicMock()
    mock_resp.choices = [
        MagicMock(message=MagicMock(content='{"score":8,"pass":true,"issues":[],"warnings":[]}'))
    ]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_resp
    mock_backend = MagicMock(client=mock_client, model="gemini-2.5-flash-lite", provider="gemini")

    with patch("shorts_bot.llm.provider.get_llm_backend", return_value=mock_backend):
        _gemini_vision_review(
            frames,
            topic="gas station horror",
            hook="streetlight flickers",
            pack_dir=pack,
        )

    prompt = mock_client.chat.completions.create.call_args.kwargs["messages"][0]["content"][0]["text"]
    assert "youtube.com/shorts/R7cEIG_gqLU" in prompt
    assert "LIGHTS ARE OFF" in prompt
