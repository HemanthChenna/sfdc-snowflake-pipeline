"""Tiny JSON-file watermark store. Swap for a Snowflake table in production."""
import json
from pathlib import Path
from src.config import DEFAULT_WATERMARK


class WatermarkStore:
    def __init__(self, path="state/watermarks.json"):
        self.path = Path(path)

    def _read(self) -> dict:
        return json.loads(self.path.read_text()) if self.path.exists() else {}

    def get(self, obj: str) -> str:
        return self._read().get(obj, DEFAULT_WATERMARK)

    def set(self, obj: str, value: str) -> None:
        state = self._read()
        state[obj] = value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(state, indent=2))
