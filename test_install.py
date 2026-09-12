"""Run with: python test_install.py"""

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "install.py"
EXPECTED = [
    Path("AGENTS.md"),
    Path(".codex/config.toml"),
    *(Path(".codex/agents") / name for name in ("architect.toml", "builder.toml", "researcher.toml", "runner.toml", "scout.toml")),
    Path(".agents/skills/quota-orchestrator/SKILL.md"),
]


def run(target, *args, success=True):
    result = subprocess.run([sys.executable, str(SCRIPT), *args, str(target)], capture_output=True, text=True)
    assert (result.returncode == 0) == success, result.stdout + result.stderr
    return result


def snapshot(root):
    return {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="codexskills-install-") as temporary:
        base = Path(temporary)

        empty = base / "empty"
        empty.mkdir()
        run(empty)
        assert all((empty / path).is_file() for path in EXPECTED)
        assert "codexskills:routing-b:start" in (empty / "AGENTS.md").read_text(encoding="utf-8")
        assert not (empty / "README.md").exists()
        first = snapshot(empty)
        run(empty)
        assert snapshot(empty) == first

        existing = base / "existing"
        (existing / ".codex/agents").mkdir(parents=True)
        original_agents = "# user rules\n"
        original_config = '# keep this comment\nmodel = "user-model"\ncustom = 7\n\n[features]\ncustom = true\n'
        (existing / "AGENTS.md").write_text(original_agents, encoding="utf-8")
        (existing / ".codex/config.toml").write_text(original_config, encoding="utf-8")
        custom_agent = existing / ".codex/agents/scout.toml"
        custom_agent.write_text('name = "local scout"\n', encoding="utf-8")
        result = run(existing)
        merged_agents = (existing / "AGENTS.md").read_text(encoding="utf-8")
        merged_config = (existing / ".codex/config.toml").read_text(encoding="utf-8")
        assert merged_agents.startswith(original_agents) and merged_agents.count("codexskills:routing-b:start") == 1
        assert '# keep this comment' in merged_config and 'model = "user-model"' in merged_config
        assert "custom = 7" in merged_config and "custom = true" in merged_config
        assert "multi_agent = true" in merged_config and "[agents]" in merged_config
        assert custom_agent.read_text(encoding="utf-8") == 'name = "local scout"\n'
        assert "préservé avec avertissement" in result.stdout
        assert list((existing / ".codexskills-backup").glob("*/AGENTS.md"))
        before = snapshot(existing)
        second = run(existing)
        assert "bloc codexskills existant" not in second.stderr
        after = snapshot(existing)
        assert after == before, {
            "added": sorted(map(str, after.keys() - before.keys())),
            "changed": sorted(str(path) for path in after.keys() & before.keys() if after[path] != before[path]),
        }

        override = base / "override"
        override.mkdir()
        (override / "AGENTS.override.md").write_text("override\n", encoding="utf-8")
        run(override)
        assert "codexskills:routing-b:start" in (override / "AGENTS.override.md").read_text(encoding="utf-8")
        assert not (override / "AGENTS.md").exists()

        dry = base / "dry"
        dry.mkdir()
        run(dry, "--dry-run")
        assert snapshot(dry) == {}

        invalid = base / "invalid"
        (invalid / ".codex").mkdir(parents=True)
        (invalid / ".codex/config.toml").write_text("broken = [", encoding="utf-8")
        run(invalid, success=False)
        assert set(snapshot(invalid)) == {Path(".codex/config.toml")}

        linked_target = base / "linked-target"
        linked_source = base / "linked-source"
        linked_source.mkdir()
        try:
            linked_target.symlink_to(linked_source, target_is_directory=True)
        except OSError:
            pass
        else:
            run(linked_target, success=False)
            assert snapshot(linked_source) == {}

        spec = importlib.util.spec_from_file_location("codexskills_installer", SCRIPT)
        installer = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = installer
        spec.loader.exec_module(installer)
        rollback = base / "rollback"
        rollback.mkdir()
        actions, _, _ = installer.plan(rollback)
        real_write = installer._write
        calls = 0

        def fail_second(path, content, replace):
            global calls
            calls += 1
            if calls == 2:
                raise OSError("simulated")
            real_write(path, content, replace)

        with patch.object(installer, "_write", fail_second):
            try:
                installer.apply(rollback, actions)
            except OSError:
                pass
            else:
                raise AssertionError("rollback failure was not raised")
        assert not any((rollback / path).exists() for path in EXPECTED)
        assert list(rollback.iterdir()) == []

    print("PASS: empty install, merge, conflicts, override, idempotence, dry-run, invalid TOML, symlink refusal, rollback.")
