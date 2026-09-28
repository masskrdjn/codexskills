#!/usr/bin/env python3
"""Best-effort, offline SessionStart reconciliation of bundled global profiles."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import install as installer

SOURCE = ROOT / "templates"


def digest(paths: list[Path], root: Path) -> str:
    result = hashlib.sha256()
    for path in paths:
        installer._check_path(root, path)
        result.update(path.relative_to(root).as_posix().encode("utf-8"))
        result.update(b"\0")
        if path.exists():
            if not path.is_file():
                raise installer.InstallError(f"{path}: un fichier était attendu")
            result.update(hashlib.sha256(path.read_bytes()).digest())
        else:
            result.update(b"missing")
    return result.hexdigest()


def source_digest() -> str:
    return digest(
        [ROOT / ".codex-plugin/plugin.json", ROOT / "scripts/install.py", ROOT / "hooks/reconcile.py",
         SOURCE / "AGENTS.md", SOURCE / ".codex/config.toml", *installer._managed_sources()],
        ROOT,
    )


def target_paths(target: Path) -> list[Path]:
    agents = target / ("AGENTS.override.md" if (target / "AGENTS.override.md").exists() else "AGENTS.md")
    return [
        agents, target / "config.toml",
        *(target / "agents" / source.name for source in installer._managed_sources() if source.suffix == ".toml"),
        target / "skills/quota-orchestrator/SKILL.md",
    ]


def reconcile(target: Path, data_dir: Path) -> None:
    if installer._unsafe(target):
        raise installer.InstallError(f"{target}: symlink/junction refusé")
    if not target.is_dir():
        raise installer.InstallError(f"{target}: CODEX_HOME doit exister")
    target = target.resolve()
    if installer._unsafe(data_dir):
        raise installer.InstallError(f"{data_dir}: symlink/junction refusé")
    data_dir.mkdir(parents=True, exist_ok=True)
    state_path = data_dir / "reconcile-state.json"
    lock_path = data_dir / "reconcile.lock"
    if installer._unsafe(state_path) or installer._unsafe(lock_path):
        raise installer.InstallError(f"{data_dir}: état ou verrou lié refusé")

    # Atomic mkdir serializes sessions. An abandoned lock is recoverable.
    deadline = time.monotonic() + 5
    while True:
        try:
            lock_path.mkdir()
            break
        except FileExistsError:
            if installer._unsafe(lock_path) or not lock_path.is_dir():
                raise installer.InstallError(f"{lock_path}: verrou invalide")
            if time.time() - lock_path.stat().st_mtime > 300:
                try:
                    lock_path.rmdir()
                except OSError:
                    pass
            if time.monotonic() >= deadline:
                raise installer.InstallError("une autre session réconcilie déjà les profils ; prochain démarrage réessaiera")
            time.sleep(0.1)

    try:
        desired = {"schema": 1, "target": str(target), "source_digest": source_digest(),
                   "target_digest": digest(target_paths(target), target)}
        try:
            state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
        except (ValueError, UnicodeError):
            state = {}
        if state == desired:
            return

        actions, _, warnings = installer.plan(target, global_scope=True)
        backup = installer.apply(target, actions)
        for warning in warnings:
            print(f"codexskills: avertissement: {warning}", file=sys.stderr)
        if actions:
            print(f"codexskills: {len(actions)} fichier(s) réconcilié(s); ouvrir une nouvelle tâche pour les charger", file=sys.stderr)
        if backup:
            print(f"codexskills: sauvegarde: {backup}", file=sys.stderr)

        desired["target_digest"] = digest(target_paths(target), target)
        handle, temporary = tempfile.mkstemp(prefix=".reconcile-state.", dir=data_dir)
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                json.dump(desired, stream, sort_keys=True)
            os.replace(temporary, state_path)
        except Exception:
            Path(temporary).unlink(missing_ok=True)
            raise
    finally:
        lock_path.rmdir()


def main() -> int:
    target = Path(os.environ["CODEX_HOME"]).expanduser() if os.environ.get("CODEX_HOME") else Path.home() / ".codex"
    data_dir = Path(os.environ.get("PLUGIN_DATA") or target / ".codexskills-data").expanduser()
    try:
        reconcile(target, data_dir)
    except Exception as exc:
        # A hook must not prevent Codex from starting. The next session retries.
        print(f"codexskills: réconciliation différée: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
