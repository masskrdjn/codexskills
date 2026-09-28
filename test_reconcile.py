"""Run with: python test_reconcile.py"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent
PLUGIN = ROOT / "plugins/codexskills"
SCRIPT = PLUGIN / "hooks/reconcile.py"


def run(home, data):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        env={**os.environ, "CODEX_HOME": str(home), "PLUGIN_DATA": str(data)},
    )


def snapshot(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="codexskills-reconcile-") as temporary:
        base = Path(temporary)
        home = base / "home"
        data = base / "data"
        home.mkdir()
        first = run(home, data)
        assert first.returncode == 0, first.stderr
        assert "réconcilié" in first.stderr
        assert (home / "agents/architect.toml").is_file()
        assert (home / "skills/quota-orchestrator/SKILL.md").is_file()
        state = json.loads((data / "reconcile-state.json").read_text(encoding="utf-8"))
        assert state["schema"] == 1
        assert not (data / "reconcile.lock").exists()
        files = snapshot(home)
        second = run(home, data)
        assert second.returncode == 0 and not second.stderr and not second.stdout
        assert snapshot(home) == files

        custom = home / "agents/scout.toml"
        custom.write_text('name = "my scout"\n', encoding="utf-8")
        changed = run(home, data)
        assert changed.returncode == 0 and "avertissement" in changed.stderr
        assert custom.read_text(encoding="utf-8") == 'name = "my scout"\n'
        assert run(home, data).stderr == ""

        blocked_home = base / "blocked"
        blocked_home.mkdir()
        (blocked_home / "config.toml").write_text("broken = [", encoding="utf-8")
        failed = run(blocked_home, base / "blocked-data")
        assert failed.returncode == 0 and "réconciliation différée" in failed.stderr
        assert not (base / "blocked-data/reconcile-state.json").exists()

        lock_data = base / "lock-data"
        lock_data.mkdir()
        lock = lock_data / "reconcile.lock"
        lock.mkdir()
        os.utime(lock, (time.time() - 600, time.time() - 600))
        recovered = run(home, lock_data)
        assert recovered.returncode == 0 and not lock.exists()

        spec = importlib.util.spec_from_file_location("codexskills_reconcile_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        old = b'name = "old exact scout"\n'
        custom.write_bytes(old)
        with patch.dict(module.installer.LEGACY_SHA256, {
            ".codex/agents/scout.toml": __import__("hashlib").sha256(old).hexdigest()
        }):
            module.reconcile(home, base / "upgrade-data")
        assert custom.read_bytes() == (PLUGIN / "templates/.codex/agents/scout.toml").read_bytes()
        assert list((home / ".codexskills-backup").glob("*/agents/scout.toml"))

    print("PASS: hook reconciliation, no-op, divergence, failure, stale lock, exact upgrade.")
