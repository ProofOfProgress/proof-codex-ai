"""Legacy homemade render pipeline — retired in favor of InVideo."""

from __future__ import annotations


class LegacyPipelineRetired(RuntimeError):
    """Raised when code paths for Blender/Kling/Recraft render are invoked."""

    def __init__(self, detail: str = "") -> None:
        msg = (
            "Homemade render pipeline retired (Blender, Kling, Recraft, jumpscare). "
            "Use PIPELINE_BACKEND=invideo and shorts_bot.invideo.* instead."
        )
        if detail:
            msg = f"{msg} ({detail})"
        super().__init__(msg)
