"""Harbor Godot prompt identity vs host 1Game-neutral copy."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.verifier.judges import _common
from gamecraft_bench.verifier.judges.base import JudgeRequest, RequirementSpec


def test_placeholder_secrets_rejected() -> None:
    assert _common.is_placeholder_secret("your_openai_api_key_here")
    assert _common.is_placeholder_secret("changeme")
    assert not _common.is_placeholder_secret("sk-real-token-value")


def test_godot_default_keeps_godot_copy() -> None:
    text = _common.system_instruction()
    assert "Godot 2D game" in text
    assert text == _common.SYSTEM_INSTRUCTION
    assert _common.playthrough_noun() == "Godot 2D game"
    assert _common.system_instruction(engine="godot") == _common.SYSTEM_INSTRUCTION


def test_1game_prompt_is_neutral() -> None:
    text = _common.system_instruction(engine="1game")
    assert "Godot" not in text
    assert "a 2D game" in text
    assert _common.playthrough_noun(engine="1game") == "2D game"
    assert _common.SYSTEM_INSTRUCTION != text


def test_judge_request_engine_default_is_godot() -> None:
    req = JudgeRequest(
        demo_id="d",
        video_path=Path("x.mp4"),
        frame_paths=[],
        requirements=[RequirementSpec(id="M1", description="x")],
    )
    assert req.engine == "godot"
    req2 = JudgeRequest(
        demo_id="d",
        video_path=Path("x.mp4"),
        frame_paths=[],
        requirements=[RequirementSpec(id="M1", description="x")],
        engine="1game",
    )
    assert req2.engine == "1game"
