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


SOURCE = Path(__file__).resolve().parent
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
# Exact GPT-6 files distributed in 0.4.0, before the Luna builder update.
PREVIOUS_SHA256 = {
    ".codex/agents/builder.toml": "88be0cb3fbe1b2427b5e94e2869ee5fecfa48719a45530786939ffb158fd1250",
    ".agents/skills/quota-orchestrator/SKILL.md": "a7fd75994b7076bf9c982a25579c104d11e7456db42e4d02889574d06832c790",
}
# Exact files distributed in 0.5.0, before the Sol builder and strategist.
RELEASE_0_5_SHA256 = {
    ".codex/agents/builder.toml": "31e154b6a6ee67caab4bc3c25fdb674d073f89c879ec83f64e560e6a09a9c60b",
    ".agents/skills/quota-orchestrator/SKILL.md": "1bdf0be6aa75e6784ff79bbd924846671e1f9f3df9ace1471ca0a52320c66e12",
}
# Exact files distributed in 0.7.0, before task-based selection and the Luna floor.
RELEASE_0_7_SHA256 = {
    ".codex/config.toml": "d5376090d44478d616ee2a73c980b3de73bbaacfac2a08f7a2bd0cbcd6b3e6f1",
    ".codex/agents/runner.toml": "026a979e24747f720dd5bf74bc8836e38883aa298ec8ebaf9234de753e86d8ec",
    ".codex/agents/researcher.toml": "44c189b44a09fb0c6993af108c4701a1ad33a7973ba2764729146800c03cbf54",
    "AGENTS.md": "7a452e7c86674371591b45ed2d825e2225c2d3a223d2cb6c765c2a61fbfa2b85",
    ".agents/skills/quota-orchestrator/SKILL.md": "f31101d44017be19531d4b048a751cab3fb238d93c490ac4b4296ff7006c9864",
    ".codex/agents/builder.toml": "b08f4657f1a0ac70e4bd0b3ff9fc1fb238aac99539146d39111080063d783aff",
    ".codex/agents/strategist.toml": "8bf9f04eae36817bd54fd25c7b97a05d6c98322f998472c538e218424b4db7c0",
    ".codex/agents/scout_complex.toml": "bf161c784d8cc131442f6723ed36374a03669aca886a641e94a10070b51fcf16",
    ".codex/agents/researcher_complex.toml": "bcdee495e761d517ff22f370dceca38cf0d3c79ba1cabd8e89c649b4daf1a5cb",
}
# Authentic 0.8.0 distribution, preserved in fixtures/release_0_8_0.
RELEASE_0_8_SHA256 = {
    "AGENTS.md": "3e4a19d21cdcbc6308d229c9183f9f84806164d1835f50ab376d7dedb2a77ea8",
    ".codex/config.toml": "629e472aa2b829045dd08d5090973fb1d5d74f718e52d55e50fccd3925dd38dc",
    ".codex/agents/architect.toml": "26d902b1539fdcad6cee13bfaecdd0a97179f983408b4e983e9d4d3f06c3d061",
    ".codex/agents/builder.toml": "c0fa44686cd79eae3ce5d47fa07653d35713eb3267e8bbc218efea5a72536fc4",
    ".codex/agents/researcher.toml": "4f7985baf06881e9476222a89a81a5532fa407e6f5bc8781334b48ecab895e2e",
    ".codex/agents/researcher_complex.toml": "75ef288f755f1fb496e7d6aea8d797fede9c5cc39c78fb5d468129dd55195db9",
    ".codex/agents/runner.toml": "b4ba262b78798c57692db57b115b81971c31ec085d9dc64346ae2ff3dce6232d",
    ".codex/agents/scout.toml": "12137ef6e7cea9311e4c4a075e816ffafe7752ee054e49a32d1f4b5aecc610db",
    ".codex/agents/scout_complex.toml": "64ca07998abdb1694d112a0d40f5d4f88fb00312e07c0dcb60e8c223eace23e3",
    ".codex/agents/strategist.toml": "34f50d8c6757a76c56c51a089d2599904ac3836ce98d0dda9b635661b7b2a4d3",
    ".agents/skills/quota-orchestrator/SKILL.md": "9724896967c1861c03fa87c3930260d1fe5f368244a283fddae35a7aedd80735",
}
RELEASE_0_8_AGENTS_BLOCK_SHA256 = "780fbcfa4a6dac1eca2d01c15ee83c9944b436a4c4ed846a490ae4864ab1c670"
# 0.8.1 as first published (b6d823d); 443ab80 then changed these two files under the same version.
RELEASE_0_8_1_SHA256 = {
    "AGENTS.md": "555118857e37ac24f433b479412f8b652d9a59563300c0b3058499d75248832c",
    ".agents/skills/quota-orchestrator/SKILL.md": "d240146e364cc7bb6ef5a3bd1ffac9755172a1237e402e0917bed2d99addcf55",
}
RELEASE_0_8_1_AGENTS_BLOCK_SHA256 = "d0d2c469abe122649756c7d782e5ea6254f93122ce410ef63fd70a94fd5c2092"
RELEASE_0_7_AGENTS_BLOCK_SHA256 = "ed3a2cef5b69b266d417e970e8ef2533cd4a400eb121b34e8c537fa425888d91"
LEGACY_AGENTS_BLOCK_SHA256 = "cead871fee8a8ae0179552d16770ab0344d7869de9d24c3fdbc58ef1cf4c86e5"
RELEASE_0_5_AGENTS_BLOCK_SHA256 = "290aa11f0c6a6fd45c0a013b85a9bd11b488d1fc4c7412b63c2c64a18a7d0ec9"
# The wait bounds are one atomic group: Codex refuses a configuration unless min <= default <= max,
# so they are added only when the user has none of the three and defines multi_agent_v2 nowhere else.
WAIT_SECTION = ("features", "multi_agent_v2")
CONFIG_KEYS = {
    (): ("approval_policy", "sandbox_mode"),
    ("features",): ("multi_agent",),
    ("agents",): (
        "enabled",
        "max_concurrent_threads_per_session",
        "default_subagent_model",
        "default_subagent_reasoning_effort",
    ),
    WAIT_SECTION: ("min_wait_timeout_ms", "default_wait_timeout_ms", "max_wait_timeout_ms"),
}
TABLE_RE = re.compile(r"^\s*\[([A-Za-z0-9_-]+(?:[.][A-Za-z0-9_-]+)*)]\s*(?:#.*)?$")
KEY_RE = re.compile(r"^\s*([A-Za-z0-9_-]+)\s*=")


def _table(match) -> tuple[str, ...]:
    return tuple(match.group(1).split("."))


class InstallError(Exception):
    pass


@dataclass
class Action:
    path: Path
    content: bytes
    status: str


def _is_legacy(path: str, content: bytes) -> bool:
    digest = hashlib.sha256(content.replace(b"\r\n", b"\n")).hexdigest()
    return digest in (
        LEGACY_SHA256.get(path),
        PREVIOUS_SHA256.get(path),
        RELEASE_0_5_SHA256.get(path),
        RELEASE_0_7_SHA256.get(path),
        RELEASE_0_8_SHA256.get(path),
        RELEASE_0_8_1_SHA256.get(path),
    )


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
            section = _table(match)
        elif match := KEY_RE.match(line):
            key = match.group(1)
            if section in CONFIG_KEYS and key in CONFIG_KEYS[section]:
                found[(section, key)] = line.strip()
    expected = {(section, key) for section, keys in CONFIG_KEYS.items() for key in keys}
    if found.keys() != expected:
        raise InstallError(f".codex/config.toml source ne contient pas les {len(expected)} clés attendues")
    return found


def _upgrade_default_model(text: str) -> str:
    lines = text.splitlines(keepends=True)
    section: tuple[str, ...] | None = ()
    for index, line in enumerate(lines):
        raw = line.rstrip("\r\n")
        if header := TABLE_RE.match(raw):
            section = _table(header)
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
    has_wait_header = any(
        (match := TABLE_RE.match(line.rstrip("\r\n"))) and _table(match) == WAIT_SECTION
        for line in target_text.splitlines()
    )
    features = target_tree.get("features")
    wait_defined = isinstance(features, dict) and "multi_agent_v2" in features
    wait_present = any(_value(target_tree, WAIT_SECTION, key)[0] for key in CONFIG_KEYS[WAIT_SECTION])
    wait_blocked = wait_present or (wait_defined and not has_wait_header)

    for section, keys in CONFIG_KEYS.items():
        for key in keys:
            source_present, source_value = _value(source_tree, section, key)
            target_present, target_value = _value(target_tree, section, key)
            assert source_present
            dotted = ".".join((*section, key))
            if not target_present:
                if section == WAIT_SECTION:
                    if wait_blocked:
                        continue
                    missing.setdefault(section, []).append(assignments[(section, key)])
                    continue
                missing.setdefault(section, []).append(assignments[(section, key)])
            elif target_value != source_value:
                warnings.append(
                    f"{path}: {dotted} conservé ({target_value!r}, valeur proposée {source_value!r})"
                )

    if wait_blocked and any(not _value(target_tree, WAIT_SECTION, key)[0] for key in CONFIG_KEYS[WAIT_SECTION]):
        warnings.append(
            f"{path}: features.multi_agent_v2 déjà configuré : plancher d'attente de cinq minutes non ajouté"
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
            headers.append((index, _table(match) if match else None))

    inserts: list[tuple[int, int, str]] = []  # (line, 0 = into an existing table / 1 = new table, text)
    if root_lines := missing.get(()) :
        index = headers[0][0] if headers else len(lines)
        inserts.append((index, 0, newline.join(root_lines) + newline))

    for section in (name for name in CONFIG_KEYS if name):
        values = missing.get(section)
        if not values:
            continue
        matching = [position for position, name in headers if name == section]
        if matching:
            start = matching[0]
            index = next((position for position, _ in headers if position > start), len(lines))
            inserts.append((index, 0, newline.join(values) + newline))
        else:
            existing = target_tree.get(section[0])
            # A table known only through dotted headers ([features.x]) can be declared later with its own header.
            implicit = isinstance(existing, dict) and all(
                isinstance(value, dict) and any(name is not None and name[:2] == (section[0], key) for _, name in headers)
                for key, value in existing.items()
            )
            if len(section) == 1 and section[0] in target_tree and not implicit:
                raise InstallError(f"{path}: section {section[0]!r} impossible à localiser pour une fusion sûre")
            prefix = "" if not lines or lines[-1].endswith(("\n", "\r")) else newline
            inserts.append((len(lines), 1, f"{prefix}{newline}[{'.'.join(section)}]{newline}" + newline.join(values) + newline))

    # Keys going into an existing table must land before any new table appended at the same line.
    for index, _, addition in reversed(sorted(inserts, key=lambda item: item[:2])):
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
        old_digest = hashlib.sha256(old_block.encode("utf-8")).hexdigest()
        if old_digest in (LEGACY_AGENTS_BLOCK_SHA256, RELEASE_0_5_AGENTS_BLOCK_SHA256, RELEASE_0_7_AGENTS_BLOCK_SHA256, RELEASE_0_8_AGENTS_BLOCK_SHA256, RELEASE_0_8_1_AGENTS_BLOCK_SHA256):
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
