---
name: quota-orchestrator-setup
description: Required one-time setup after installing codexskills. Install or update the complete scout, researcher, runner, builder, and architect Codex profiles globally. Use when the user asks to configure, install, update, or preview full routing, in English or French.
---

# Configure the complete profiles

This is the required one-time global setup after plugin installation. The
plugin contains a non-destructive installer and every required configuration
template. The user does not need to edit any TOML file manually. Communicate
in the user's language.

## Procedure

1. Resolve the plugin root from this file: walk upward from
   `skills/quota-orchestrator-setup/SKILL.md` to the root containing
   `scripts/install.py`.
2. Run:

   `python <plugin-root>/scripts/install.py --global --dry-run`

   When the user explicitly requests migration to the new GPT-6 default,
   append `--upgrade-default-model` to this dry run and to the apply command.
   The flag changes only `agents.default_subagent_model` when its current value
   is exactly `gpt-5.6-luna`; other configuration remains intact.

3. Briefly present creations, upgrades, merges, preserved files, and warnings.
4. If the user explicitly asked to install, configure, or update, proceed with
   the safe actions shown by the dry run without another confirmation:

   `python <plugin-root>/scripts/install.py --global`

5. Keep divergent files unchanged and report precisely which ones need manual
   adaptation. Never overwrite them to silence a warning.
6. Report created, upgraded, or merged files and every backup location. Then prominently
   ask the user to open a new Codex task so instructions and profiles reload.

## Guarantees

- Install globally by default in `CODEX_HOME`, or `~/.codex` when
  `CODEX_HOME` is unset. The layout is `AGENTS.md`, `config.toml`,
  `agents/`, and `skills/` directly under that directory.
- For an explicit project-only installation, run
  `python <plugin-root>/scripts/install.py <project-root>` outside this
  plugin setup workflow.
- Never bypass a symlink or junction refusal.
- Upgrade only an exact match to a previously distributed profile, with a
  backup. Never overwrite a customized or unknown profile.
- Do not edit `AGENTS.md`, `.codex/config.toml`, or profiles directly when the
  installer can perform the controlled merge.
- Do not use an installation hook or run setup without an explicit user
  request.
