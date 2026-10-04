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

        # Authentic 0.8.0 reconciliation, exact backup, then a silent no-op.
        release_home = base / "release-0.8-home"
        release_home.mkdir()
        fixtures = ROOT / "fixtures/release_0_8_0"
        templates = fixtures / "plugins/codexskills/templates"
        originals = {}
        for source in templates.rglob("*"):
            if not source.is_file():
                continue
            relative = source.relative_to(templates)
            if relative == Path(".codex/config.toml"):
                relative = Path("config.toml")
            elif relative.parts[:2] == (".codex", "agents"):
                relative = Path("agents") / source.name
            elif relative.parts[0] == ".agents":
                relative = Path("skills/quota-orchestrator/SKILL.md")
            raw = (fixtures / "managed_AGENTS.md").read_bytes() if relative == Path("AGENTS.md") else source.read_bytes()
            path = release_home / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            originals[relative] = raw
        release_data = base / "release-0.8-data"
        migrated = run(release_home, release_data)
        assert migrated.returncode == 0 and "réconcilié" in migrated.stderr
        assert "avertissement" not in migrated.stderr
        backups = list((release_home / ".codexskills-backup").iterdir())
        assert len(backups) == 1
        for relative, raw in originals.items():
            if (release_home / relative).read_bytes() != raw:
                assert (backups[0] / relative).read_bytes() == raw, relative
        assert "pas en nombre de tokens" in (release_home / "AGENTS.md").read_text(encoding="utf-8")
        upgraded = snapshot(release_home)
        no_op = run(release_home, release_data)
        assert no_op.returncode == 0 and not no_op.stderr and not no_op.stdout
        assert snapshot(release_home) == upgraded
        print("PASS: authentic 0.8.0 SessionStart migration, exact backups and silent second run.")


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

        # Upgrade exact 0.7.0 profiles, including the Luna effort floor.
        for role, model, effort in (
            ("builder", "gpt-6-sol", "high"),
            ("strategist", "gpt-5.6-sol", "medium"),
            ("scout_complex", "gpt-6-sol", "high"),
            ("researcher_complex", "gpt-6-sol", "max"),
            ("runner", "gpt-6-luna", "medium"),
            ("researcher", "gpt-6-luna", "max"),
        ):
            source = PLUGIN / f"templates/.codex/agents/{role}.toml"
            # Preserve the preexisting 0.7.0 regression using authentic 0.8.0 text.
            current = (ROOT / "fixtures/release_0_8_0" / source.relative_to(ROOT)).read_text(encoding="utf-8")
            previous = current.replace("gpt-6.1-sol", model).replace(
                'model_reasoning_effort = "xhigh"',
                f'model_reasoning_effort = "{effort}"',
            )
            if role in ("runner", "researcher"):
                previous = previous.replace(
                    'model_reasoning_effort = "high"',
                    f'model_reasoning_effort = "{effort}"',
                )
            previous = previous.encode("utf-8")
            assert module.installer._is_legacy(f".codex/agents/{role}.toml", previous)
            (home / f"agents/{role}.toml").write_bytes(previous)
        config_source = PLUGIN / "templates/.codex/config.toml"
        # The previous (0.8.x) config has no wait bounds: cut the block this release appended.
        previous_config = config_source.read_text(encoding="utf-8").split("\n# Attente d'un enfant", 1)[0].replace(
            "# Routage sélectif; secours provisoires, sans optimum mesuré.",
            "# Routage sélectif, runner optimisé après comparaison.",
        ).replace('default_subagent_reasoning_effort = "high"',
                  'default_subagent_reasoning_effort = "max"').encode("utf-8")
        assert module.installer._is_legacy(".codex/config.toml", previous_config)
        (home / "config.toml").write_bytes(previous_config)
        module.reconcile(home, base / "sol-upgrade-data")
        assert (home / "config.toml").read_bytes() == config_source.read_bytes()
        assert list((home / ".codexskills-backup").glob("*/config.toml"))
        for role in ("builder", "strategist", "scout_complex", "researcher_complex", "runner", "researcher"):
            source = PLUGIN / f"templates/.codex/agents/{role}.toml"
            target = home / f"agents/{role}.toml"
            assert target.read_bytes() == source.read_bytes()
            assert list((home / ".codexskills-backup").glob(f"*/agents/{role}.toml"))
        assert custom.read_bytes() == (PLUGIN / "templates/.codex/agents/scout.toml").read_bytes()

        # A personalized effort below the floor stays intact with a warning.
        runner = home / "agents/runner.toml"
        personalized = runner.read_text(encoding="utf-8").replace(
            'model_reasoning_effort = "high"', 'model_reasoning_effort = "low"'
        ) + "\n# personal setting\n"
        runner.write_text(personalized, encoding="utf-8")
        result = run(home, base / "personal-effort-data")
        assert result.returncode == 0 and "avertissement" in result.stderr
        assert runner.read_text(encoding="utf-8") == personalized

    print("PASS: hook reconciliation, no-op, divergence, failure, stale lock, exact upgrade, 0.7.0 profiles, config and custom Luna effort preservation.")
