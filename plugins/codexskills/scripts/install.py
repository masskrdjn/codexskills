#!/usr/bin/env python3
"""Install this repository's Codex routing files without overwriting user data."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


SOURCE = Path(__file__).resolve().parent.parent / "templates"
START = "<!-- codexskills:routing-b:start -->"
END = "<!-- codexskills:routing-b:end -->"
# SHA-256 of the files distributed before the GPT-6 profile update, with line
# endings normalized. Otherwise an exact match is required; custom files stay.
LEGACY_SHA256 = {
    "AGENTS.md": "414984acf4ad2c0041457352cd39aecd5c3888e3ad2949cd6c3450e3fa748ce2",
    ".codex/config.toml": "efed1cea98ed0f720146608acc45a8a93cd005205155e88cba0e0039e40ca1e9",
    ".codex/agents/scout.toml": "e53e685a8bdc90c149c37638f6864cb5148ba9ac25e91900ad6e660a234e00ef",
    ".codex/agents/researcher.toml": "00685b081a56cd340690797d7d3357a322df73d422a228df567de966e5a8bfc0",
    ".codex/agents/runner.toml": "f19f39d0e22dd2abccc4631c036b5f56fdce5e50c82f13ca2fe5bec22f61beb3",
    ".codex/agents/builder.toml": "7c53784264bc2e7cead54bc195a397f49462cd15b80af4f2ae65bc42e661d1de",
    ".codex/agents/architect.toml": "83a6ab62026f719599de86c4f81e5845108439d1654700ddf4005dce28442b33",
    ".agents/skills/quota-orchestrator/SKILL.md": "4a9bbfb7e6d5fe020ed82011880ae88711ca456f5d81cb7097358621057981cd",
}
LEGACY_AGENTS_BLOCK_SHA256 = "cead871fee8a8ae0179552d16770ab0344d7869de9d24c3fdbc58ef1cf4c86e5"
CONFIG_KEYS = {
    (): ("approval_policy", "sandbox_mode"),
    ("features",): ("multi_agent",),
    ("agents",): (
        "enabled",
        "max_concurrent_threads_per_session",
        "default_subagent_model",
        "default_subagent_reasoning_effort",
    ),
}
TABLE_RE = re.compile(r"^\s*\[([A-Za-z0-9_-]+)]\s*(?:#.*)?$")
KEY_RE = re.compile(r"^\s*([A-Za-z0-9_-]+)\s*=")


class InstallError(Exception):
    pass


@dataclass
class Action:
    path: Path
    content: bytes
    status: str


def _is_legacy(path: str, content: bytes) -> bool:
    return hashlib.sha256(content.replace(b"\r\n", b"\n")).hexdigest() == LEGACY_SHA256.get(path)


def _decode(data: bytes, path: Path) -> tuple[str, bool]:
    bom = data.startswith(b"\xef\xbb\xbf")
    try:
        return data.decode("utf-8-sig"), bom
    except UnicodeDecodeError as exc:
        raise InstallError(f"{path}: UTF-8 invalide") from exc


def _encode(text: str, bom: bool) -> bytes:
    data = text.encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def _parse_toml(data: bytes, path: Path) -> dict:
    text, _ = _decode(data, path)
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise InstallError(f"{path}: TOML invalide: {exc}") from exc


def _value(tree: dict, section: tuple[str, ...], key: str):
    node = tree
    for part in section:
        node = node.get(part, {})
        if not isinstance(node, dict):
            return False, None
    return (key in node, node.get(key))


def _source_assignments(text: str) -> dict[tuple[tuple[str, ...], str], str]:
    section: tuple[str, ...] = ()
    found = {}
    for line in text.splitlines():
        if match := TABLE_RE.match(line):
            section = (match.group(1),)
        elif match := KEY_RE.match(line):
            key = match.group(1)
            if section in CONFIG_KEYS and key in CONFIG_KEYS[section]:
                found[(section, key)] = line.strip()
    expected = {(section, key) for section, keys in CONFIG_KEYS.items() for key in keys}
    if found.keys() != expected:
        raise InstallError(".codex/config.toml source ne contient pas les sept clés attendues")
    return found


def _upgrade_default_model(text: str) -> str:
    lines = text.splitlines(keepends=True)
    section: tuple[str, ...] | None = ()
    for index, line in enumerate(lines):
        raw = line.rstrip("\r\n")
        if header := TABLE_RE.match(raw):
            section = (header.group(1),)
        elif raw.lstrip().startswith("["):
            section = None
        elif section == ("agents",) and (key := KEY_RE.match(raw)) and key.group(1) == "default_subagent_model":
            assignment = re.fullmatch(
                r"(\s*default_subagent_model\s*=\s*)['\"]gpt-5\.6-luna['\"](\s*(?:#.*)?)", raw
            )
            if assignment:
                lines[index] = f'{assignment.group(1)}"gpt-6-luna"{assignment.group(2)}{line[len(raw):]}'
            break
    return "".join(lines)


def _merge_config(source: bytes, target: bytes, path: Path, upgrade_default_model: bool = False) -> tuple[bytes, list[str]]:
    if _is_legacy(".codex/config.toml", target):
        return source, []
    source_tree = _parse_toml(source, SOURCE / ".codex/config.toml")
    target_tree = _parse_toml(target, path)
    source_text, _ = _decode(source, SOURCE / ".codex/config.toml")
    target_text, bom = _decode(target, path)
    if upgrade_default_model and _value(target_tree, ("agents",), "default_subagent_model") == (True, "gpt-5.6-luna"):
        updated_text = _upgrade_default_model(target_text)
        if updated_text != target_text:
            target_text = updated_text
            target = _encode(target_text, bom)
            target_tree = _parse_toml(target, path)
    assignments = _source_assignments(source_text)
    missing: dict[tuple[str, ...], list[str]] = {}
    warnings = []

    for section, keys in CONFIG_KEYS.items():
        for key in keys:
            source_present, source_value = _value(source_tree, section, key)
            target_present, target_value = _value(target_tree, section, key)
            assert source_present
            dotted = ".".join((*section, key))
            if not target_present:
                missing.setdefault(section, []).append(assignments[(section, key)])
            elif target_value != source_value:
                warnings.append(
                    f"{path}: {dotted} conservé ({target_value!r}, valeur proposée {source_value!r})"
                )

    if not missing:
        return target, warnings
    if "'''" in target_text or '\"\"\"' in target_text:
        raise InstallError(f"{path}: chaînes multilignes non prises en charge pour une fusion sûre")

    lines = target_text.splitlines(keepends=True)
    newline = "\r\n" if "\r\n" in target_text else "\n"
    headers: list[tuple[int, tuple[str, ...] | None]] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("["):
            match = TABLE_RE.match(line.rstrip("\r\n"))
            headers.append((index, (match.group(1),) if match else None))

    inserts: list[tuple[int, str]] = []
    if root_lines := missing.get(()) :
        index = headers[0][0] if headers else len(lines)
        inserts.append((index, newline.join(root_lines) + newline))

    for section in (("features",), ("agents",)):
        values = missing.get(section)
        if not values:
            continue
        matching = [position for position, name in headers if name == section]
        if matching:
            start = matching[0]
            index = next((position for position, _ in headers if position > start), len(lines))
            inserts.append((index, newline.join(values) + newline))
        else:
            if section[0] in target_tree:
                raise InstallError(f"{path}: section {section[0]!r} impossible à localiser pour une fusion sûre")
            prefix = "" if not lines or lines[-1].endswith(("\n", "\r")) else newline
            inserts.append((len(lines), f"{prefix}{newline}[{section[0]}]{newline}" + newline.join(values) + newline))

    for index, addition in reversed(sorted(inserts, key=lambda item: item[0])):
        lines[index:index] = [addition]
    merged = _encode("".join(lines), bom)
    _parse_toml(merged, path)
    return merged, warnings


def _merge_agents(source: bytes, target: bytes, path: Path) -> tuple[bytes, list[str]]:
    if target == source:
        return target, []
    if _is_legacy("AGENTS.md", target):
        return source, []
    source_text, _ = _decode(source, SOURCE / "AGENTS.md")
    target_text, bom = _decode(target, path)
    newline = "\r\n" if "\r\n" in target_text else "\n"
    block = source_text.replace("\r\n", "\n").rstrip("\n").replace("\n", newline)
    if START in target_text or END in target_text:
        if START not in target_text or END not in target_text:
            raise InstallError(f"{path}: marqueurs codexskills incomplets")
        if f"{START}{newline}{block}{newline}{END}" in target_text:
            return target, []
        start = target_text.index(START) + len(START)
        end = target_text.index(END, start)
        old_block = target_text[start:end].strip("\r\n").replace("\r\n", "\n")
        if hashlib.sha256(old_block.encode("utf-8")).hexdigest() == LEGACY_AGENTS_BLOCK_SHA256:
            merged = target_text[:start] + newline + block + newline + target_text[end:]
            return _encode(merged, bom), []
        return target, [f"{path}: bloc codexskills existant conservé car il diffère de la source"]
    separator = "" if not target_text else (newline if target_text.endswith(("\n", "\r")) else newline * 2)
    merged = f"{target_text}{separator}{START}{newline}{block}{newline}{END}{newline}"
    return _encode(merged, bom), []


def _managed_sources() -> list[Path]:
    return [
        *sorted((SOURCE / ".codex/agents").glob("*.toml")),
        SOURCE / ".agents/skills/quota-orchestrator/SKILL.md",
    ]


def _unsafe(path: Path) -> bool:
    return path.is_symlink() or bool(getattr(os.path, "isjunction", lambda _: False)(path))


def _check_path(target: Path, path: Path) -> None:
    current = target
    if _unsafe(current):
        raise InstallError(f"{current}: symlink/junction refusé")
    parts = path.relative_to(target).parts
    for index, part in enumerate(parts):
        current /= part
        if current.exists() and _unsafe(current):
            raise InstallError(f"{current}: symlink/junction refusé")
        if current.exists() and index < len(parts) - 1 and not current.is_dir():
            raise InstallError(f"{current}: un répertoire était attendu")


def plan(target: Path, global_scope: bool = False, upgrade_default_model: bool = False) -> tuple[list[Action], list[tuple[str, Path]], list[str]]:
    if not target.exists() or not target.is_dir():
        raise InstallError(f"{target}: la cible doit être un répertoire existant")
    target = target.resolve()
    actions: list[Action] = []
    unchanged: list[tuple[str, Path]] = []
    warnings: list[str] = []

    agents_target = target / ("AGENTS.override.md" if (target / "AGENTS.override.md").exists() else "AGENTS.md")
    _check_path(target, agents_target)
    source_agents = (SOURCE / "AGENTS.md").read_bytes()
    if agents_target.exists():
        if not agents_target.is_file():
            raise InstallError(f"{agents_target}: un fichier était attendu")
        original = agents_target.read_bytes()
        merged, notes = _merge_agents(source_agents, original, agents_target)
        warnings.extend(notes)
        if merged != original:
            actions.append(Action(agents_target, merged, "fusionné"))
        else:
            unchanged.append(("déjà présent", agents_target))
    else:
        managed, _ = _merge_agents(source_agents, b"", agents_target)
        actions.append(Action(agents_target, managed, "créé"))

    source_config_path = SOURCE / ".codex/config.toml"
    source_config = source_config_path.read_bytes()
    _parse_toml(source_config, source_config_path)
    config_target = target / ("config.toml" if global_scope else ".codex/config.toml")
    _check_path(target, config_target)
    if config_target.exists():
        if not config_target.is_file():
            raise InstallError(f"{config_target}: un fichier était attendu")
        original = config_target.read_bytes()
        merged, notes = _merge_config(source_config, original, config_target, upgrade_default_model)
        warnings.extend(notes)
        if merged != original:
            actions.append(Action(config_target, merged, "fusionné"))
        else:
            unchanged.append(("déjà présent", config_target))
    else:
        actions.append(Action(config_target, source_config, "créé"))

    for source in _managed_sources():
        if source.suffix == ".toml":
            _parse_toml(source.read_bytes(), source)
        if global_scope:
            destination = (
                target / "agents" / source.name
                if source.suffix == ".toml"
                else target / "skills/quota-orchestrator/SKILL.md"
            )
        else:
            destination = target / source.relative_to(SOURCE)
        _check_path(target, destination)
        if destination.exists():
            if not destination.is_file():
                raise InstallError(f"{destination}: un fichier était attendu")
            existing = destination.read_bytes()
            updated = source.read_bytes()
            if existing == updated:
                unchanged.append(("déjà présent", destination))
            elif _is_legacy(source.relative_to(SOURCE).as_posix(), existing):
                actions.append(Action(destination, updated, "mis à niveau"))
            else:
                unchanged.append(("préservé avec avertissement", destination))
                warnings.append(f"{destination}: fichier personnalisé ou inconnu conservé ; adaptation manuelle nécessaire")
        else:
            actions.append(Action(destination, source.read_bytes(), "créé"))
    return actions, unchanged, warnings


def _write(path: Path, content: bytes, replace: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not replace:
        with path.open("xb") as stream:
            stream.write(content)
        return
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(content)
        shutil.copymode(path, temporary)
        os.replace(temporary, path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def apply(target: Path, actions: list[Action]) -> Path | None:
    changed = [action for action in actions if action.path.exists()]
    backup = None
    if changed:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = target / ".codexskills-backup" / stamp
        for action in changed:
            saved = backup / action.path.relative_to(target)
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(action.path, saved)

    created: list[Path] = []
    created_dirs: set[Path] = set()
    try:
        for action in actions:
            existed = action.path.exists()
            parent = action.path.parent
            while not parent.exists() and parent != target:
                created_dirs.add(parent)
                parent = parent.parent
            _write(action.path, action.content, existed)
            if not existed:
                created.append(action.path)
        for action in actions:
            if action.path.suffix == ".toml":
                _parse_toml(action.path.read_bytes(), action.path)
    except Exception:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        for path in sorted(created_dirs, key=lambda item: len(item.parts), reverse=True):
            try:
                path.rmdir()
            except OSError:
                pass
        if backup:
            for action in changed:
                shutil.copy2(backup / action.path.relative_to(target), action.path)
        raise
    return backup


def install(target: Path, dry_run: bool = False, global_scope: bool = False, upgrade_default_model: bool = False) -> int:
    if _unsafe(target):
        raise InstallError(f"{target}: symlink/junction refusé")
    target = target.resolve()
    actions, unchanged, warnings = plan(target, global_scope, upgrade_default_model)
    backup = None if dry_run else apply(target, actions)
    prefix = "[dry-run] " if dry_run else ""
    scope = "globale" if global_scope else "projet"
    print(f"{prefix}portée: {scope} — destination: {target}")
    for action in actions:
        print(f"{prefix}{action.status}: {action.path.relative_to(target)}")
    for status, path in unchanged:
        print(f"{status}: {path.relative_to(target)}")
    for warning in warnings:
        print(f"avertissement: {warning}", file=sys.stderr)
    if dry_run and any(action.path.exists() for action in actions):
        print(f"[dry-run] sauvegarde: {target / '.codexskills-backup' / '<horodatage>'}")
    if backup:
        print(f"sauvegarde: {backup}")
    print(f"résumé: {len(actions)} changement(s), {len(unchanged)} fichier(s) conservé(s), {len(warnings)} avertissement(s)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", type=Path, help="répertoire du projet (défaut: courant)")
    parser.add_argument("--global", dest="global_scope", action="store_true", help="installer dans CODEX_HOME (ou ~/.codex)")
    parser.add_argument("--dry-run", action="store_true", help="afficher le plan sans écrire")
    parser.add_argument("--upgrade-default-model", action="store_true", help="migrer explicitement l'ancien modèle générique GPT-5.6 Luna vers GPT-6 Luna")
    args = parser.parse_args()
    if args.global_scope and args.target is not None:
        parser.error("--global ne peut pas être combiné avec une cible projet")
    target = (
        Path(os.environ["CODEX_HOME"]).expanduser()
        if args.global_scope and os.environ.get("CODEX_HOME")
        else Path.home() / ".codex"
        if args.global_scope
        else args.target or Path.cwd()
    )
    try:
        return install(target, args.dry_run, args.global_scope, args.upgrade_default_model)
    except (InstallError, OSError) as exc:
        print(f"erreur: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
