"""Run with: python -m unittest discover -s tests -p '*_test.py'."""

import copy
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/codexskills"
SCRIPT = PLUGIN / "hooks/check_delegation.py"
spec = importlib.util.spec_from_file_location("delegation_guard", SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class DelegationGuard(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="codexskills-guard-", dir=ROOT)
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.home = self.base / "home"
        self.cwd = self.base / "project"
        self.home.mkdir()
        self.cwd.mkdir()
        self.trust_project()
        self.transcript = self.base / "session.jsonl"
        self.context = {"turn_id": "turn-1", "cwd": str(self.cwd),
                        "model": "gpt-6.1-sol", "effort": "high"}
        self.write_context()
        self.event = {"hook_event_name": "PreToolUse", "tool_name": "spawn_agent",
                      "session_id": "session-1", "turn_id": "turn-1",
                      "model": "gpt-6.1-sol", "cwd": str(self.cwd),
                      "transcript_path": str(self.transcript),
                      "tool_input": {"agent_type": "builder", "fork_turns": "none"}}
        self.profile("builder", "gpt-6.1-sol", "high")
        self.profile("builder_luna", "gpt-6-luna", "max")
        self.profile("researcher", "gpt-6-luna", "high")

    def write_context(self, extra=()):
        records = [{"type": "session_meta", "payload": {"id": "session-1"}},
                   {"type": "turn_context", "payload": self.context}, *extra]
        self.transcript.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")

    def profile(self, role, model=None, effort=None, directory=None, filename=None):
        directory = (directory or self.home) / "agents"
        directory.mkdir(parents=True, exist_ok=True)
        fields = {"name": role, "description": "fixture", "developer_instructions": "fixture"}
        if model is not None:
            fields["model"] = model
        if effort is not None:
            fields["model_reasoning_effort"] = effort
        path = directory / (filename or f"{role}.toml")
        path.write_text("".join(f"{key} = {json.dumps(value)}\n" for key, value in fields.items()), encoding="utf-8")
        return path

    def run_hook(self, event=None, raw=None):
        result = subprocess.run([sys.executable, str(SCRIPT)],
                                input=raw if raw is not None else json.dumps(event or self.event),
                                encoding="utf-8", capture_output=True, timeout=5,
                                env={**os.environ, "CODEX_HOME": str(self.home)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        if result.stdout:
            output = json.loads(result.stdout)["hookSpecificOutput"]
            self.assertEqual(output["hookEventName"], "PreToolUse")
            self.assertEqual(output["permissionDecision"], "deny")
            self.assertNotIn(str(self.base), result.stdout)
            return output["permissionDecisionReason"]
        return None

    def test_screenshot_builder_is_denied(self):
        self.assertIn("même modèle et même effort", self.run_hook())

    def test_luna_is_allowed(self):
        self.event["tool_input"]["agent_type"] = "researcher"
        self.assertIsNone(self.run_hook())

    def test_luna_max_builder_is_allowed(self):
        self.event["tool_input"]["agent_type"] = "builder_luna"
        self.assertIsNone(self.run_hook())

    def test_different_effort_is_allowed(self):
        self.profile("builder", "gpt-6.1-sol", "medium")
        self.assertIsNone(self.run_hook())

    def test_profile_overrides_explicit_spawn_values(self):
        self.event["tool_input"].update(model="gpt-6-luna", reasoning_effort="low")
        self.assertIn("même modèle", self.run_hook())

    def test_aliases_and_json_arguments(self):
        for name in ("Agent", "collaboration.spawn_agent", "functions.spawn_agent", "collaborationspawn_agent"):
            with self.subTest(name=name):
                event = copy.deepcopy(self.event)
                event["tool_name"] = name
                event["tool_input"] = json.dumps(event["tool_input"])
                self.assertIn("même modèle", self.run_hook(event))

    def test_non_spawn_tools_are_untouched(self):
        self.assertIsNone(self.run_hook({"tool_name": "Bash"}))

    def test_invalid_input_denies_instead_of_failing_the_hook(self):
        for raw in ("", "{", "null", "[]", "x" * (guard.MAX_INPUT + 1)):
            with self.subTest(raw=raw[:12]):
                self.assertIn("refusée", self.run_hook(raw=raw))

    def test_missing_fields_deny(self):
        for name in ("model", "turn_id", "session_id", "cwd", "transcript_path", "tool_name", "tool_input"):
            with self.subTest(name=name):
                event = copy.deepcopy(self.event)
                del event[name]
                self.assertIn("refusée", self.run_hook(event))

    def test_wrong_session_turn_or_model_denies(self):
        for name, value in (("session_id", "other"), ("turn_id", "other"), ("model", "gpt-6-astra")):
            with self.subTest(name=name):
                event = copy.deepcopy(self.event)
                event[name] = value
                self.assertIn("refusée", self.run_hook(event))

    def test_latest_context_must_match_not_an_older_turn(self):
        self.write_context([{"type": "turn_context", "payload": {**self.context, "turn_id": "new-turn"}}])
        self.assertIn("périmé", self.run_hook())

    def test_missing_effort_and_contradictory_context_deny(self):
        del self.context["effort"]
        self.write_context()
        self.assertIn("refusée", self.run_hook())
        self.context["effort"] = "high"
        self.context["collaboration_mode"] = {"settings": {"reasoning_effort": "low"}}
        self.write_context()
        self.assertIn("contradictoires", self.run_hook())

    def test_message_text_cannot_supply_turn_settings(self):
        self.transcript.write_text(json.dumps({"type": "session_meta", "payload": {"id": "session-1"}}) + "\n" +
                                   json.dumps({"type": "response_item", "payload": {"text": json.dumps(self.context)}}),
                                   encoding="utf-8")
        self.assertIn("introuvable", self.run_hook())

    def test_corrupt_context_denies(self):
        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write('{"type":"turn_context","payload":')
        self.assertIn("incomplet", self.run_hook())

    def test_open_transcript_and_partial_unrelated_tail(self):
        self.event["tool_input"]["agent_type"] = "researcher"
        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write('{"type":"response_item"')
            stream.flush()
            self.assertIsNone(self.run_hook())

    def test_tail_scan_is_bounded(self):
        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write(" " * (64 * 1024 + 1))
        with patch.object(guard, "MAX_SCAN", 64 * 1024):
            with self.assertRaisesRegex(guard.Unresolved, "borne"):
                guard.check(self.event, self.home)

    def test_unknown_and_partial_profiles_deny(self):
        self.event["tool_input"]["agent_type"] = "unknown"
        self.assertIn("introuvable", self.run_hook())
        self.profile("unknown", "gpt-6-luna")
        self.assertIn("partiel", self.run_hook())

    def test_builtin_explicit_settings(self):
        self.event["tool_input"] = {"agent_type": "worker", "fork_turns": "none", "model": "gpt-6.1-sol", "reasoning_effort": "high"}
        self.assertIn("même modèle", self.run_hook())
        self.event["tool_input"]["model"] = "gpt-6-luna"
        self.assertIsNone(self.run_hook())

    def test_defaults_are_not_assumed_to_be_live_settings(self):
        self.trust_project('[agents]\ndefault_subagent_model="gpt-6-luna"\n'
                           'default_subagent_reasoning_effort="high"\n')
        self.event["tool_input"] = {"agent_type": "default", "fork_turns": "none"}
        self.assertIn("explicite", self.run_hook())

    def test_full_fork_is_not_guessed(self):
        self.event["tool_input"] = {"agent_type": "researcher", "fork_turns": "all"}
        self.assertIn("héritage", self.run_hook())

    def test_unspecified_fork_is_not_assumed_to_be_none(self):
        del self.event["tool_input"]["fork_turns"]
        self.assertIn("héritage absent", self.run_hook())

    def test_profile_name_not_filename_selects_agent(self):
        (self.home / "agents/researcher.toml").rename(self.home / "agents/arbitrary-filename.toml")
        self.event["tool_input"]["agent_type"] = "researcher"
        self.assertIsNone(self.run_hook())

    def test_legacy_config_file_is_relative_to_its_declaration(self):
        self.trust_project('[agents.legacy]\nconfig_file="custom.toml"\n')
        (self.home / "custom.toml").write_text('model="gpt-6.1-sol"\nmodel_reasoning_effort="high"\n', encoding="utf-8")
        self.event["tool_input"]["agent_type"] = "legacy"
        self.assertIn("même modèle", self.run_hook())

    def trust_project(self, config=""):
        (self.home / "config.toml").write_text(config + f'[projects.{json.dumps(str(self.cwd))}]\ntrust_level="trusted"\n', encoding="utf-8")

    def test_trusted_project_profile(self):
        self.trust_project()
        self.profile("project_agent", "gpt-6-luna", "high", self.cwd / ".codex")
        self.event["tool_input"]["agent_type"] = "project_agent"
        self.assertIsNone(self.run_hook())

    def test_untrusted_project_and_conflicting_layers_deny(self):
        (self.home / "config.toml").unlink()
        self.profile("builder", "gpt-6-luna", "high", self.cwd / ".codex")
        self.assertIn("confiance", self.run_hook())
        self.trust_project()
        self.assertIn("contradictoires", self.run_hook())

    def test_duplicate_profiles_and_bad_toml_deny(self):
        path = self.profile("builder", "gpt-6-luna", "high", filename="duplicate.toml")
        self.assertIn("contradictoires", self.run_hook())
        path.write_text("model = [", encoding="utf-8")
        self.assertIn("format", self.run_hook())

    def test_nearest_untrusted_project_cannot_inherit_outer_trust(self):
        self.profile("builder", "gpt-6.1-sol", "high", self.cwd / ".codex")
        nested = self.cwd / "nested"
        nested.mkdir()
        with (self.home / "config.toml").open("a", encoding="utf-8") as stream:
            stream.write(f'[projects.{json.dumps(str(nested))}]\ntrust_level="untrusted"\n')
        self.event["cwd"] = self.context["cwd"] = str(nested)
        self.write_context()
        self.assertIn("confiance", self.run_hook())

    def test_oversized_config_denies_before_parsing(self):
        (self.home / "agents/builder.toml").write_text(" " * (guard.MAX_INPUT + 1), encoding="utf-8")
        self.assertIn("volumineuse", self.run_hook())

    def test_registered_command_and_matcher(self):
        hooks = json.loads((PLUGIN / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]
        group = hooks["PreToolUse"][0]
        for name in ("spawn_agent", "Agent", "collaboration.spawn_agent", "collaborationspawn_agent"):
            self.assertRegex(name, re.compile(group["matcher"]))
        self.assertIsNone(re.search(group["matcher"], "exec_command"))
        handler = group["hooks"][0]
        self.assertNotIn("async", handler)
        self.assertEqual(handler["command"], 'python "${PLUGIN_ROOT}/hooks/check_delegation.py"')
        self.assertEqual(len(hooks["SessionStart"]), 1)


if __name__ == "__main__":
    unittest.main()
