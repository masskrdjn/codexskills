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



def exercise_authentic_0_8_upgrade(base):
    """Both entry points, project/global, exact backups, no-op and customs."""
    fixtures = ROOT / "fixtures/release_0_8_0"
    templates = fixtures / "plugins/codexskills/templates"
    checked = 0
    for index, script in enumerate((SCRIPT, ROOT / "plugins/codexskills/scripts/install.py")):
        for global_scope in (False, True):
            target = base / f"release-0.8-{index}-{global_scope}"
            target.mkdir()
            old_files = {}
            destinations = {}
            for source in templates.rglob("*"):
                if not source.is_file():
                    continue
                relative = source.relative_to(templates)
                if global_scope:
                    if relative == Path(".codex/config.toml"):
                        relative = Path("config.toml")
                    elif relative.parts[:2] == (".codex", "agents"):
                        relative = Path("agents") / source.name
                    elif relative.parts[0] == ".agents":
                        relative = Path("skills/quota-orchestrator/SKILL.md")
                data = source.read_bytes()
                if relative == Path("AGENTS.md"):
                    data = b"# user prefix\n" + (fixtures / "managed_AGENTS.md").read_bytes() + b"# user suffix\n"
                path = target / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                old_files[relative] = data
                destinations[relative] = ROOT / "plugins/codexskills/templates" / source.relative_to(templates)

            def invoke():
                args = [sys.executable, str(script)]
                environment = {**__import__("os").environ, "CODEX_HOME": str(target)}
                args += ["--global"] if global_scope else [str(target)]
                result = subprocess.run(args, capture_output=True, text=True, env=environment)
                assert result.returncode == 0, result.stdout + result.stderr
                return result

            first = invoke()
            assert not first.stderr, first.stderr
            assert "sauvegarde:" in first.stdout
            backup_dirs = list((target / ".codexskills-backup").iterdir())
            assert len(backup_dirs) == 1
            for relative, old_data in old_files.items():
                current = (target / relative).read_bytes()
                if current != old_data:
                    assert (backup_dirs[0] / relative).read_bytes() == old_data, relative
                if relative != Path("AGENTS.md"):
                    assert current == destinations[relative].read_bytes(), relative
            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            assert agents.startswith("# user prefix\n") and agents.endswith("# user suffix\n")
            assert "pas en nombre de tokens" in agents
            upgraded = snapshot(target)
            second = invoke()
            assert not second.stderr and "résumé: 0 changement(s)" in second.stdout
            assert snapshot(target) == upgraded

            # All genuinely customized 0.8.0 roles and the skill stay byte-exact.
            for relative, old_data in old_files.items():
                if relative.name == "config.toml":
                    custom = old_data.replace(b'default_subagent_reasoning_effort = "high"', b'default_subagent_reasoning_effort = "low"')
                elif relative == Path("AGENTS.md"):
                    custom = old_data.replace(b"<!-- codexskills:routing-b:end -->", b"# personalized managed rule\n<!-- codexskills:routing-b:end -->")
                else:
                    custom = old_data + b"\n# genuine user customization\n"
                (target / relative).write_bytes(custom)
            customized = snapshot(target)
            preserved = invoke()
            assert "avertissement" in preserved.stderr
            # The only change is the merge of the missing wait bounds into the user's config.
            assert "résumé: 1 changement(s)" in preserved.stdout
            after = snapshot(target)
            config_name = Path("config.toml") if global_scope else Path(".codex/config.toml")
            for relative, data in customized.items():
                if relative != config_name:
                    assert after[relative] == data, relative
            merged_config = after[config_name].decode("utf-8")
            assert 'default_subagent_reasoning_effort = "low"' in merged_config, "the user's own value is kept"
            assert "min_wait_timeout_ms = 300000" in merged_config and "max_wait_timeout_ms = 3600000" in merged_config
            checked += 1
    print(f"PASS: authentic 0.8.0 upgrade, exact backups, no-op and custom preservation ({checked} installer/scope combinations).")

def exercise_wait_bounds_merge(installer):
    """The wait bounds are one atomic group: Codex rejects a configuration unless min <= default <= max."""
    import tomllib

    source = (ROOT / ".codex/config.toml").read_bytes()
    proposed = tomllib.loads(source.decode("utf-8"))["features"]["multi_agent_v2"]
    assert proposed == {"min_wait_timeout_ms": 300000, "default_wait_timeout_ms": 300000, "max_wait_timeout_ms": 3600000}

    def bounds_ok(tree):
        wait = tree.get("features", {}).get("multi_agent_v2")
        if not isinstance(wait, dict):
            return True
        low, default, high = (wait.get(key) for key in ("min_wait_timeout_ms", "default_wait_timeout_ms", "max_wait_timeout_ms"))
        values = [value for value in (low, default, high) if value is not None]
        return (all(10000 <= value <= 3600000 for value in values) and (low is None or default is None or low <= default)
                and (default is None or high is None or default <= high) and (low is None or high is None or low <= high))

    def unchanged(user, merged, name, path=""):
        for key, value in user.items():
            assert key in merged, (name, path + key)
            if isinstance(value, dict):
                unchanged(value, merged[key], name, path + key + ".")
            else:
                assert merged[key] == value, (name, path + key)

    nl = chr(10)
    cases = {
        "empty": ("", True),
        "features only": ("[features]" + nl + "multi_agent = true" + nl, True),
        "user config": ('model = "x"' + nl + nl + "[features]" + nl + "multi_agent = true" + nl + "custom = 1" + nl + nl + "[agents]" + nl + "enabled = true" + nl, True),
        "own full trio": ("[features.multi_agent_v2]" + nl + "min_wait_timeout_ms = 480000" + nl + "default_wait_timeout_ms = 480000" + nl + "max_wait_timeout_ms = 900000" + nl, False),
        "only a low max": ("[features.multi_agent_v2]" + nl + "max_wait_timeout_ms = 120000" + nl, False),
        "table with enabled only": ("[features.multi_agent_v2]" + nl + "enabled = true" + nl, True),
        "dotted table after [features]": ("[features]" + nl + "custom = 1" + nl + "[features.multi_agent_v2]" + nl + "enabled = true" + nl, True),
        "agents first": ("[agents]" + nl + "enabled = true" + nl + nl + "[features.multi_agent_v2]" + nl + "enabled = true" + nl, True),
        "boolean flag": ("[features]" + nl + "multi_agent = true" + nl + "multi_agent_v2 = true" + nl, False),
        "dotted key without header": ("[features]" + nl + "multi_agent = true" + nl + "multi_agent_v2.enabled = true" + nl, False),
        "inline table": ("[features]" + nl + "multi_agent = true" + nl + "multi_agent_v2 = { enabled = true }" + nl, False),
    }
    for name, (target, receives_bounds) in cases.items():
        merged, warnings = installer._merge_config(source, target.encode("utf-8"), Path("config.toml"))
        tree = tomllib.loads(merged.decode("utf-8"))
        unchanged(tomllib.loads(target), tree, name)
        assert bounds_ok(tree), name
        misplaced = [key for table in ("agents", "features") for key in tree.get(table, {}) if key.endswith("_wait_timeout_ms")]
        assert not misplaced, (name, misplaced)
        wait = tree["features"].get("multi_agent_v2")
        assert (isinstance(wait, dict) and set(proposed) <= set(wait) and all(wait[key] == proposed[key] for key in proposed)) == receives_bounds, (name, wait)
        assert installer._merge_config(source, merged, Path("config.toml"))[0] == merged, f"{name}: not idempotent"
        if not receives_bounds and not isinstance(wait, dict) or name in ("own full trio", "only a low max", "dotted key without header", "inline table", "boolean flag"):
            assert warnings, f"{name}: the user must be told why the wait bounds were not added"
    bom, crlf = installer._merge_config(source, b"" + bytes([0xEF, 0xBB, 0xBF]) + b"[features]" + bytes([13, 10]) + b"multi_agent = true" + bytes([13, 10]), Path("config.toml"))
    assert bom.startswith(bytes([0xEF, 0xBB, 0xBF])) and tomllib.loads(bom.decode("utf-8-sig"))["features"]["multi_agent_v2"] == proposed
    print("PASS: wait bounds merged only as a whole group, never over the user's own bounds, and never into another table.")


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
        exercise_wait_bounds_merge(installer)
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

        exercise_authentic_0_8_upgrade(base)

    print("PASS: project/global install, merge, conflicts, override, idempotence, dry-run, invalid TOML, symlink refusal, rollback.")
