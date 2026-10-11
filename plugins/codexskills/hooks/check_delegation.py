#!/usr/bin/env python3
"""Offline PreToolUse guard: refuse identical or unprovable agent settings.

The hook event exposes the active model, but not its reasoning effort. Read
only the latest turn_context in the matching transcript, never message text.
Custom agent layers override explicit spawn settings in current Codex. We do
not infer live defaults from config.toml: a CLI/session override can change
them. An allowed spawn must have an unambiguous, fully specified custom
profile or an explicit model AND effort without a custom profile.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

MAX_INPUT = 1024 * 1024
MAX_SCAN = 32 * 1024 * 1024
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
BUILTINS = {"default", "worker", "explorer"}
# Namespaced function calls in this Codex build concatenate the namespace
# and tool name in hook events (confirmed by the offline native test).
SPAWN = re.compile(r"(?:^|[.:])spawn_agent$|^collaborationspawn_agent$|^Agent$")


class Unresolved(ValueError):
    """The effective settings cannot be established safely."""


def slug(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Unresolved(f"{label} absent ou invalide")
    value = value.strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9._:/-]*", value):
        raise Unresolved(f"{label} invalide")
    if value in {"auto", "default", "inherit", "latest"}:
        raise Unresolved(f"{label} non explicite")
    return value


def effort(value: Any) -> str:
    result = slug(value, "effort")
    if result not in EFFORTS:
        raise Unresolved("effort non reconnu")
    return result


def same_path(left: Any, right: Path) -> bool:
    return isinstance(left, str) and Path(left).resolve() == right.resolve()


def reverse_lines(path: Path):
    """Read a bounded tail, including transcripts currently open by Codex."""
    with path.open("rb") as stream:
        stream.seek(0, os.SEEK_END)
        position, scanned, pending = stream.tell(), 0, b""
        while position:
            size = min(position, 64 * 1024)
            if scanned + size > MAX_SCAN:
                raise Unresolved("contexte du tour hors de la borne de lecture")
            position -= size
            scanned += size
            stream.seek(position)
            parts = (stream.read(size) + pending).split(b"\n")
            pending = parts[0]
            yield from reversed(parts[1:])
        if pending:
            yield pending


def parent_settings(event: dict) -> tuple[str, str, Path]:
    model = slug(event.get("model"), "modèle parent")
    turn_id, session_id = event.get("turn_id"), event.get("session_id")
    if not isinstance(turn_id, str) or not turn_id or not isinstance(session_id, str) or not session_id:
        raise Unresolved("identifiant du tour ou de la session absent")
    cwd, transcript = event.get("cwd"), event.get("transcript_path")
    if not isinstance(cwd, str) or not isinstance(transcript, str):
        raise Unresolved("répertoire ou journal absent")
    cwd, path = Path(cwd).resolve(), Path(transcript)
    if not path.is_absolute() or not cwd.is_dir():
        raise Unresolved("répertoire ou journal invalide")
    with path.open("rb") as stream:
        header = json.loads(stream.readline(MAX_INPUT))
    if header.get("type") != "session_meta" or header.get("payload", {}).get("id") != session_id:
        raise Unresolved("journal d'une autre session")

    for raw in reverse_lines(path):
        # Ignore a trailing, partially flushed record and unrelated messages.
        # A malformed context record is an error, never an older-context fallback.
        if b'"turn_context"' not in raw:
            continue
        try:
            record = json.loads(raw)
        except (ValueError, UnicodeError):
            raise Unresolved("contexte du journal incomplet") from None
        if record.get("type") != "turn_context":
            continue
        context = record.get("payload", {})
        if context.get("turn_id") != turn_id:
            raise Unresolved("contexte du tour courant absent (journal périmé)")
        if slug(context.get("model"), "modèle du journal") != model or not same_path(context.get("cwd"), cwd):
            raise Unresolved("modèle ou répertoire du journal différent du tour actif")
        root_effort = effort(context.get("effort"))
        settings = context.get("collaboration_mode", {}).get("settings", {})
        if settings.get("reasoning_effort") is not None and effort(settings["reasoning_effort"]) != root_effort:
            raise Unresolved("efforts contradictoires dans le contexte")
        if context.get("profile") or context.get("config_profile"):
            raise Unresolved("profil de session non résolu")
        return model, root_effort, cwd
    raise Unresolved("contexte du tour courant introuvable")


def read_toml(path: Path) -> dict:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        raise Unresolved("configuration liée non résolue")
    with path.open("rb") as stream:
        raw = stream.read(MAX_INPUT + 1)
    if len(raw) > MAX_INPUT:
        raise Unresolved("configuration trop volumineuse")
    return tomllib.loads(raw.decode("utf-8"))


def layers(home: Path, cwd: Path) -> list[tuple[Path, dict]]:
    """Only load project layers explicitly covered by a trusted project."""
    user = read_toml(home / "config.toml") if (home / "config.toml").exists() else {}
    result = [(home, user)]
    projects = []
    for name, settings in user.get("projects", {}).items():
        if isinstance(settings, dict):
            root = Path(name).resolve()
            if cwd == root or root in cwd.parents:
                projects.append((root, settings.get("trust_level")))
    closest = max(projects, key=lambda item: len(item[0].parts)) if projects else None
    trust_root = closest[0] if closest is not None and closest[1] == "trusted" else None
    for directory in reversed((cwd, *cwd.parents)):
        config_dir = directory / ".codex"
        if not (config_dir / "config.toml").exists() and not (config_dir / "agents").exists():
            continue
        if trust_root is not None and not (directory == trust_root or trust_root in directory.parents):
            continue
        if trust_root is None:
            # Untrusted layers are not loaded by Codex. Refuse to speculate about
            # project/session trust that wasn't persisted in the user config.
            raise Unresolved("confiance de la configuration projet non établie")
        config = read_toml(config_dir / "config.toml") if (config_dir / "config.toml").exists() else {}
        result.append((config_dir, config))
    return result


def custom_profile(role: str, scopes: list[tuple[Path, dict]]) -> dict | None:
    selected = None
    for directory, config in scopes:
        candidates = []
        declaration = config.get("agents", {}).get(role, {})
        if declaration:
            if not isinstance(declaration, dict) or not declaration.get("config_file"):
                raise Unresolved("déclaration du profil sans fichier résoluble")
            profile_path = Path(declaration["config_file"]).expanduser()
            if not profile_path.is_absolute():
                profile_path = directory / profile_path
            candidates.append(read_toml(profile_path))
        agent_dir = directory / "agents"
        if agent_dir.exists():
            if agent_dir.is_symlink() or (hasattr(agent_dir, "is_junction") and agent_dir.is_junction()):
                raise Unresolved("répertoire de profils lié")
            for path in sorted(agent_dir.glob("*.toml")):
                profile = read_toml(path)
                if profile.get("name") == role:
                    candidates.append(profile)
        if candidates:
            pairs = {(candidate.get("model"), candidate.get("model_reasoning_effort")) for candidate in candidates}
            if len(pairs) != 1:
                raise Unresolved("plusieurs définitions contradictoires du profil")
            if selected is not None and pairs != {(selected.get("model"), selected.get("model_reasoning_effort"))}:
                # Config/profile discovery order may vary across Codex versions.
                # Different project/global pairs require a verified resolver.
                raise Unresolved("profils global et projet contradictoires")
            selected = candidates[0]
    return selected


def child_settings(arguments: dict, scopes: list[tuple[Path, dict]]) -> tuple[str, str]:
    role = arguments.get("agent_type", arguments.get("subagent_type", "default"))
    if not isinstance(role, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", role):
        raise Unresolved("nom de profil invalide")
    if arguments.get("fork_turns") == "all":
        raise Unresolved("héritage intégral : réglages effectifs non prouvés")
    if arguments.get("fork_turns") != "none":
        raise Unresolved("mode d'héritage absent ou non reconnu")
    profile = custom_profile(role, scopes)
    if profile is not None:
        # Custom configuration is applied AFTER explicit/default spawn values.
        # Partial profiles would require resolving live inherited/default effort.
        if "model" not in profile or "model_reasoning_effort" not in profile:
            raise Unresolved("profil partiel : modèle et effort effectifs non prouvés")
        return slug(profile["model"], "modèle enfant"), effort(profile["model_reasoning_effort"])
    if role not in BUILTINS:
        raise Unresolved("profil personnalisé introuvable")
    requested_effort = arguments.get("reasoning_effort")
    if "model_reasoning_effort" in arguments:
        if requested_effort is not None and requested_effort != arguments["model_reasoning_effort"]:
            raise Unresolved("efforts demandés contradictoires")
        requested_effort = arguments["model_reasoning_effort"]
    return slug(arguments.get("model"), "modèle enfant explicite"), effort(requested_effort)


def check(event: dict, home: Path) -> str | None:
    if not isinstance(event, dict):
        raise Unresolved("événement invalide")
    tool = event.get("tool_name")
    if not isinstance(tool, str):
        raise Unresolved("nom d'outil absent")
    if not SPAWN.search(tool):
        return None
    if event.get("hook_event_name") != "PreToolUse":
        raise Unresolved("événement attendu : PreToolUse")
    arguments = event.get("tool_input")
    if isinstance(arguments, str):
        arguments = json.loads(arguments)
    if not isinstance(arguments, dict):
        raise Unresolved("arguments de délégation invalides")
    parent_model, parent_effort, cwd = parent_settings(event)
    child_model, child_effort = child_settings(arguments, layers(home, cwd))
    if (parent_model, parent_effort) == (child_model, child_effort):
        return (f"codexskills : délégation refusée ({parent_model}, effort {parent_effort}) : "
                "même modèle et même effort que la racine. Poursuivre à la racine.")
    return None


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(MAX_INPUT + 1)
        if len(raw) > MAX_INPUT:
            raise Unresolved("événement trop volumineux")
        event = json.loads(raw)
        home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser().resolve()
        reason = check(event, home)
    except Exception as exc:
        # Return Codex's documented deny shape, NOT a failed hook (which Codex
        # may ignore). Never include raw inputs, paths, or transcript content.
        detail = str(exc) if isinstance(exc, Unresolved) else "erreur de lecture ou de format"
        reason = f"codexskills : délégation refusée : {detail}. Réglages non prouvés ; poursuivre à la racine."
    if reason:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                         "permissionDecision": "deny", "permissionDecisionReason": reason}}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
