"""
Simple session & memory management for InterviewForge.
Persists to disk (JSON) for long-term memory and supports in-memory session for active interviews.
"""

import json
import pathlib
import time
from typing import Any, Dict, List

OUT_DIR = pathlib.Path("interviewforge_output")
OUT_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_FILE = OUT_DIR / "memory_bank.json"

class MemoryBank:
    def __init__(self, path: pathlib.Path = MEMORY_FILE):
        self.path = pathlib.Path(path)
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text())
            except Exception:
                self._data = {"runs": []}
        else:
            self._data = {"runs": []}

    def save_run(self, run: Dict[str, Any]):
        run["timestamp"] = time.time()
        self._data["runs"].append(run)
        self.path.write_text(json.dumps(self._data, indent=2))

    def list_runs(self) -> List[Dict[str, Any]]:
        return self._data.get("runs", [])

class InMemorySession:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.questions = []
        self.answers = []
        self.checkpoints = []

    def checkpoint(self):
        snap = {
            "time": time.time(),
            "questions_len": len(self.questions),
            "answers_len": len(self.answers)
        }
        self.checkpoints.append(snap)
        return snap
