"""Offline native Codex integration; set CODEX_GUARD_TEST_BINARY to enable.

A loopback Responses fixture asks the real tool dispatcher to spawn an agent.
No OpenAI credentials, remote model, or live user configuration are used.
Only the test hook's actual hash is trusted, in a disposable CODEX_HOME.
"""

import json
import os
import queue
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/codexskills/hooks/check_delegation.py"
BINARY = os.environ.get("CODEX_GUARD_TEST_BINARY")
# This catalog entry exposes direct local tools without a desktop Code Mode
# host. The model is entirely simulated; no model API is called.
PARENT_MODEL = "gpt-5.5"


def hook_metadata(binary, home, cwd):
    process = subprocess.Popen([binary, "app-server", "--listen", "stdio://"],
                               cwd=cwd, env={**os.environ, "CODEX_HOME": str(home)},
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    messages = queue.Queue()

    def read():
        for line in process.stdout:
            try:
                messages.put(json.loads(line))
            except ValueError:
                pass

    reader = threading.Thread(target=read, daemon=True)
    reader.start()

    def request(identifier, method, params):
        process.stdin.write(json.dumps({"id": identifier, "method": method, "params": params}) + "\n")
        process.stdin.flush()
        while True:
            message = messages.get(timeout=20)
            if message.get("id") == identifier:
                if "error" in message:
                    raise AssertionError(message["error"])
                return message["result"]

    try:
        request(1, "initialize", {"clientInfo": {"name": "codexskills-guard-test", "version": "0.8.4"},
                                  "capabilities": {"experimentalApi": True}})
        process.stdin.write('{"method":"initialized"}\n')
        process.stdin.flush()
        entries = request(2, "hooks/list", {"cwds": [str(cwd)]})["data"]
        errors = [error for entry in entries for error in entry["errors"]]
        if errors:
            raise AssertionError(errors)
        return [hook for entry in entries for hook in entry["hooks"]
                if hook["eventName"].replace("_", "").lower() == "pretooluse"]
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        process.stdin.close()
        process.stdout.close()
        reader.join(timeout=2)


@unittest.skipUnless(BINARY, "set CODEX_GUARD_TEST_BINARY for offline native integration")
class NativeDelegation(unittest.TestCase):
    def run_case(self, role, partial=False):
        with tempfile.TemporaryDirectory(prefix="codexskills-runtime-") as temporary:
            base = Path(temporary)
            home, cwd = base / "home", base / "project"
            home.mkdir()
            cwd.mkdir()
            (home / "agents").mkdir()
            for name, model in (("builder", PARENT_MODEL), ("researcher", "gpt-6-luna")):
                effort_line = '' if partial and name == "builder" else 'model_reasoning_effort="high"\n'
                (home / f"agents/{name}.toml").write_text(
                    f'name={json.dumps(name)}\ndescription="fixture"\ndeveloper_instructions="Return fixture done."\n'
                    f'model={json.dumps(model)}\n{effort_line}', encoding="utf-8")
            requests = []
            failures = []
            audit = home / "hook-events.jsonl"
            wrapper = home / "audit-hook.py"
            wrapper.write_text('import subprocess, sys\nfrom pathlib import Path\nraw=sys.stdin.buffer.read()\n'
                               f'with Path({str(audit)!r}).open("ab") as output: output.write(raw+b"\\n")\n'
                               f'result=subprocess.run([sys.executable,{str(SCRIPT)!r}],input=raw,capture_output=True)\n'
                               'sys.stdout.buffer.write(result.stdout)\nsys.stderr.buffer.write(result.stderr)\n'
                               'raise SystemExit(result.returncode)\n', encoding="utf-8")

            class Fixture(BaseHTTPRequestHandler):
                def log_message(self, *args):
                    pass

                def do_POST(self):
                    try:
                        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                        requests.append(body)
                        model = body["model"]
                        identifier = f"resp_{len(requests)}"
                        first = len(requests) == 1
                        if first:
                            item = {"type": "function_call", "id": "fc_guard", "call_id": "call_guard",
                                    "name": "spawn_agent", "namespace": "collaboration", "arguments": json.dumps({
                                        "task_name": "guard_fixture", "agent_type": role,
                                        "fork_turns": "none", "message": "Return fixture done."})}
                        else:
                            item = {"type": "message", "id": f"msg_{len(requests)}", "role": "assistant",
                                    "status": "completed", "content": [{"type": "output_text", "text": "fixture done"}]}
                        response = {"id": identifier, "object": "response", "model": model, "status": "completed",
                                    "output": [item], "usage": {"input_tokens": 10, "output_tokens": 10, "total_tokens": 20}}
                        events = [
                            {"type": "response.created", "response": {**response, "status": "in_progress", "output": []}},
                            {"type": "response.output_item.added", "output_index": 0,
                             "item": {**item, "arguments": ""} if first else {**item, "content": []}},
                        ]
                        if first:
                            events.append({"type": "response.function_call_arguments.delta", "item_id": item["id"],
                                           "output_index": 0, "delta": item["arguments"]})
                        else:
                            events.append({"type": "response.output_text.delta", "item_id": item["id"],
                                           "output_index": 0, "content_index": 0, "delta": "fixture done"})
                        events += [{"type": "response.output_item.done", "output_index": 0, "item": item},
                                   {"type": "response.completed", "response": response}]
                        data = "".join("data: " + json.dumps(event) + "\n\n" for event in events).encode()
                        self.send_response(200)
                        self.send_header("Content-Type", "text/event-stream")
                        self.send_header("Content-Length", str(len(data)))
                        self.end_headers()
                        self.wfile.write(data)
                    except Exception as exc:
                        failures.append(str(exc))
                        self.send_error(500)

            server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            self.addCleanup(server.server_close)
            try:
                command = f'python "{wrapper.as_posix()}"'
                matcher = json.loads((SCRIPT.parent / "hooks.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"][0]["matcher"]
                config = (f'model={json.dumps(PARENT_MODEL)}\nmodel_reasoning_effort="high"\nmodel_provider="fixture"\n'
                          'approval_policy="on-request"\nsandbox_mode="workspace-write"\n'
                          '[features]\nhooks=true\nmulti_agent=true\nmulti_agent_v2=true\n'
                          '[agents]\nenabled=true\n'
                          '[model_providers.fixture]\nname="Loopback fixture"\nwire_api="responses"\n'
                          f'base_url="http://127.0.0.1:{server.server_port}/v1"\nrequires_openai_auth=false\n'
                          f'[projects.{json.dumps(str(cwd))}]\ntrust_level="trusted"\n'
                          f'[[hooks.PreToolUse]]\nmatcher={json.dumps(matcher)}\n'
                          '[[hooks.PreToolUse.hooks]]\ntype="command"\ntimeout=10\n'
                          f'command={json.dumps(command)}\n')
                (home / "config.toml").write_text(config, encoding="utf-8")
                hooks = hook_metadata(BINARY, home, cwd)
                self.assertEqual(len(hooks), 1, hooks)
                hook = hooks[0]
                config += f'\n[hooks.state.{json.dumps(hook["key"])}]\ntrusted_hash={json.dumps(hook["currentHash"])}\n'
                (home / "config.toml").write_text(config, encoding="utf-8")
                self.assertEqual(hook_metadata(BINARY, home, cwd)[0]["trustStatus"], "trusted")
                result = subprocess.run([BINARY, "exec", "--skip-git-repo-check", "--json", "Fixture invocation."],
                                        cwd=cwd, env={**os.environ, "CODEX_HOME": str(home)},
                                        capture_output=True, encoding="utf-8", timeout=45)
                self.assertFalse(failures, failures)
                self.assertEqual(result.returncode, 0, result.stderr[-3000:] + result.stdout[-3000:])
                outputs = [item.get("output", "") for request in requests for item in request.get("input", [])
                           if item.get("type") == "function_call_output"]
                self.assertTrue(outputs, result.stdout[-3000:] + result.stderr[-2000:])
                transcripts = list((home / "sessions").rglob("*.jsonl"))
                audit_events = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()] if audit.exists() else []
                self.assertTrue(audit_events, "registered matcher must invoke the guard")
                if role == "builder":
                    reason = "profil partiel" if partial else "même modèle et même effort"
                    self.assertTrue(any(reason in str(output) for output in outputs), outputs)
                    self.assertEqual(len(transcripts), 1, "denied spawn must not create a child transcript")
                    self.assertFalse(any(request["model"] == "gpt-6-luna" for request in requests))
                else:
                    self.assertFalse(any("codexskills : délégation refusée" in str(output) for output in outputs), outputs)
                    self.assertGreaterEqual(len(transcripts), 2, "allowed spawn must create its child transcript")
                    contexts = [json.loads(line)["payload"] for path in transcripts
                                for line in path.read_text(encoding="utf-8").splitlines()
                                if json.loads(line).get("type") == "turn_context"]
                    self.assertTrue(any((context.get("model"), context.get("effort")) == ("gpt-6-luna", "high")
                                        for context in contexts), "allowed child's effective model/effort must match the profile")
            finally:
                server.shutdown()
                thread.join(timeout=3)

    def test_identical_pair_is_blocked_before_child_creation(self):
        self.run_case("builder")

    def test_luna_pair_can_create_child(self):
        self.run_case("researcher")

    def test_unresolved_profile_is_blocked_before_child_creation(self):
        self.run_case("builder", partial=True)


if __name__ == "__main__":
    unittest.main()
