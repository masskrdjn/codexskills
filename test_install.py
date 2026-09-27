"""Run with: python test_install.py"""

import importlib.util
import hashlib
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
    *(Path(".codex/agents") / name for name in ("architect.toml", "builder.toml", "researcher.toml", "researcher_complex.toml", "runner.toml", "scout.toml", "scout_complex.toml", "strategist.toml")),
    Path(".agents/skills/quota-orchestrator/SKILL.md"),
]
GLOBAL_EXPECTED = [
    Path("AGENTS.md"),
    Path("config.toml"),
    *(Path("agents") / name for name in ("architect.toml", "builder.toml", "researcher.toml", "researcher_complex.toml", "runner.toml", "scout.toml", "scout_complex.toml", "strategist.toml")),
    Path("skills/quota-orchestrator/SKILL.md"),
]


def run(target, *args, success=True):
    result = subprocess.run([sys.executable, str(SCRIPT), *args, str(target)], capture_output=True, text=True)
    assert (result.returncode == 0) == success, result.stdout + result.stderr
    return result


def run_global(home, *args, success=True):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--global", *args],
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "CODEX_HOME": str(home)},
    )
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

        custom_default = base / "custom-default"
        (custom_default / ".codex").mkdir(parents=True)
        configured = '# keep this setting\n[agents]\ndefault_subagent_model = "gpt-5.6-luna"\n'
        config_path = custom_default / ".codex/config.toml"
        config_path.write_text(configured, encoding="utf-8")
        preview = run(custom_default, "--dry-run", "--upgrade-default-model")
        assert ".codex\\config.toml" in preview.stdout
        assert config_path.read_text(encoding="utf-8") == configured
        preserved = run(custom_default)
        assert "default_subagent_model conservé" in preserved.stderr
        assert 'default_subagent_model = "gpt-5.6-luna"' in config_path.read_text(encoding="utf-8")
        assert '# keep this setting' in config_path.read_text(encoding="utf-8")
        run(custom_default, "--upgrade-default-model")
        assert '# keep this setting' in config_path.read_text(encoding="utf-8")
        assert 'default_subagent_model = "gpt-6-luna"' in config_path.read_text(encoding="utf-8")
        assert list((custom_default / ".codexskills-backup").glob("*/.codex/config.toml"))

        global_home = base / "global-home"
        global_home.mkdir()
        global_dry = run_global(global_home, "--dry-run")
        assert "portée: globale" in global_dry.stdout and str(global_home.resolve()) in global_dry.stdout
        assert snapshot(global_home) == {}
        run_global(global_home)
        assert all((global_home / path).is_file() for path in GLOBAL_EXPECTED)
        assert not (global_home / ".codex").exists() and not (global_home / ".agents").exists()
        first_global = snapshot(global_home)
        run_global(global_home)
        assert snapshot(global_home) == first_global
        run_global(global_home, str(empty), success=False)

        fallback_home = base / "fallback-home"
        fallback_codex = fallback_home / ".codex"
        fallback_codex.mkdir(parents=True)
        spec = importlib.util.spec_from_file_location("codexskills_installer_fallback", SCRIPT)
        installer = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = installer
        spec.loader.exec_module(installer)
        with patch.dict("os.environ", {"CODEX_HOME": ""}, clear=False), patch.object(Path, "home", return_value=fallback_home), patch.object(sys, "argv", [str(SCRIPT), "--global"]):
            assert installer.main() == 0
        assert all((fallback_codex / path).is_file() for path in GLOBAL_EXPECTED)

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
        legacy = base / "legacy"
        (legacy / ".codex/agents").mkdir(parents=True)
        old_config = b'[agents]\ndefault_subagent_model = "gpt-5.6-luna"\n'
        old_scout = b'name = "old scout"\n'
        old_block = "# old managed rule"
        old_agents = f"# user rule\n{installer.START}\n{old_block}\n{installer.END}\n"
        (legacy / ".codex/config.toml").write_bytes(old_config)
        (legacy / ".codex/agents/scout.toml").write_bytes(old_scout)
        (legacy / ".codex/agents/builder.toml").write_text('name = "custom builder"\n', encoding="utf-8")
        (legacy / "AGENTS.md").write_text(old_agents, encoding="utf-8")
        old_hashes = {
            ".codex/config.toml": hashlib.sha256(old_config).hexdigest(),
            ".codex/agents/scout.toml": hashlib.sha256(old_scout).hexdigest(),
        }
        with patch.dict(installer.LEGACY_SHA256, old_hashes), patch.object(
            installer, "LEGACY_AGENTS_BLOCK_SHA256", hashlib.sha256(old_block.encode()).hexdigest()
        ):
            assert installer._is_legacy(".codex/agents/scout.toml", old_scout.replace(b"\n", b"\r\n"))
            upgrades, preserved, warnings = installer.plan(legacy)
            assert {action.path.relative_to(legacy) for action in upgrades} >= {
                Path("AGENTS.md"), Path(".codex/config.toml"), Path(".codex/agents/scout.toml")
            }
            assert "mis à niveau" in {action.status for action in upgrades}
            assert any("builder.toml" in warning for warning in warnings)
            backup = installer.apply(legacy, upgrades)
            assert backup and (backup / "AGENTS.md").read_text(encoding="utf-8") == old_agents
            assert (backup / ".codex/config.toml").read_bytes() == old_config
            assert (backup / ".codex/agents/scout.toml").read_bytes() == old_scout
            assert (legacy / ".codex/agents/builder.toml").read_text(encoding="utf-8") == 'name = "custom builder"\n'
            assert "# user rule" in (legacy / "AGENTS.md").read_text(encoding="utf-8")
            assert old_block not in (legacy / "AGENTS.md").read_text(encoding="utf-8")
            repeated, _, repeated_warnings = installer.plan(legacy)
            assert not repeated and len(repeated_warnings) == 1
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

    print("PASS: project/global install, merge, conflicts, override, idempotence, dry-run, invalid TOML, symlink refusal, rollback.")
