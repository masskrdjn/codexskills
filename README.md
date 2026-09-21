# Selective Multi-Model Routing for Codex

[Français](README.fr.md)

A Codex configuration template that routes work to specialized agents only when delegation is likely to preserve quality while reducing total cost or latency. The primary agent remains responsible for decisions, integration, and user communication.

## Routing policy

Priorities, in order:

1. Preserve result quality and relevance.
2. Reduce total cost, including coordination and rework.
3. Reduce latency.

Small, bounded tasks stay with the primary agent. Delegation is used when a clearly scoped role can perform substantial work more efficiently or provide useful independent analysis.

| Role | Model | Effort | Responsibility |
| --- | --- | --- | --- |
| Primary | `gpt-5.6-sol` | `medium` | Triage, decisions, integration, and small local tasks |
| `scout` | `gpt-5.6-luna` | `high` | Read-only codebase and log exploration |
| `researcher` | `gpt-5.6-luna` | `max` | Multi-source external research |
| `runner` | `gpt-5.6-luna` | `medium` | Long validations and large mechanical batches |
| `builder` | `gpt-5.6-terra` | `medium` | Scoped implementation with targeted validation |
| `architect` | `gpt-6-astra` | `low` | Rare, bounded architecture decisions only |

The default subagent is Luna at `max` effort. Concurrency is capped at four spawned threads per session.

## Project layout

```text
.
├── AGENTS.md
├── .agents/skills/quota-orchestrator/SKILL.md
├── .agents/plugins/marketplace.json
├── plugins/codexskills/
│   ├── .codex-plugin/plugin.json
│   ├── skills/
│   │   ├── quota-orchestrator/SKILL.md
│   │   └── quota-orchestrator-setup/SKILL.md
│   ├── scripts/install.py
│   └── templates/
└── .codex/
    ├── config.toml
    └── agents/
        ├── architect.toml
        ├── builder.toml
        ├── researcher.toml
        ├── runner.toml
        └── scout.toml
```

- `AGENTS.md` defines the repository-wide routing and safety rules.
- `quota-orchestrator` decides whether delegation is worth its full cost.
- `.codex/config.toml` selects the primary model and enables multi-agent work.
- `.codex/agents/*.toml` defines each role's model, tools, limits, and reporting contract.
- `.agents/plugins/marketplace.json` exposes the repository's Codex catalog.
- `plugins/codexskills/` contains the manifest, both skills, the controlled installer, and the complete profiles distributed as templates.

## Install as a plugin

> [!IMPORTANT]
> Installing the plugin alone does not activate the five complete profiles.
> One-time global setup is required. Until it is complete, the plugin
> will say so at the start of tasks and will not claim that full routing is
> active.

From the local checkout, to test before publishing:

```text
codex plugin marketplace add .
codex plugin add codexskills@codexskills
```

After publishing the repository:

```text
codex plugin marketplace add masskrdjn/codexskills
codex plugin add codexskills@codexskills
```

As the required first step after installation, ask Codex:

```text
Configure the full codexskills profiles.
```

The setup skill previews the changes, then installs `scout`, `researcher`,
`runner`, `builder`, and `architect` in `CODEX_HOME` (or `~/.codex` when it is
unset). It merges compatible settings, backs up modified files under
`CODEX_HOME/.codexskills-backup/`, and stops on any warning or divergent
profile until you confirm. Start a new Codex task afterward to load the
profiles. Plugin installation itself makes no configuration changes and uses
no hook. After setup, routing is detected automatically; you do not need to
name the plugin in each request.

## Install without the plugin

Clone the repository into a directory you want to use as a Codex project:

```bash
git clone https://github.com/masskrdjn/codexskills.git
cd codexskills
```

Alternatively, copy or merge `AGENTS.md`, `.agents/`, and `.codex/` into the root of an existing repository, then review the configuration for that project before trusting it in Codex.

### Choose the scope: global, project, or both

You do **not** need to copy this entire repository into every project. Choose the placement that matches the rule:

| Scope | Put here | Use it for |
| --- | --- | --- |
| Global | Your Codex home directory (normally `~/.codex/`) | Personal defaults that should apply in every repository. Put shared instructions in `AGENTS.md`, shared settings in `config.toml`, and reusable skills in `skills/`. |
| Project | The repository root | Rules, settings, skills, and agent roles that belong only to that codebase. Use this repository's `AGENTS.md`, `.agents/`, and `.codex/` layout as the template. |
| Hybrid (recommended) | Both locations | Keep the routing policy and defaults global; add only project-specific commands, conventions, restrictions, and overrides to the repository. |

Codex loads global instructions first, then the project instructions from the repository root toward the current directory. The closest project file takes precedence. Likewise, `.codex/config.toml` can override user settings, but Codex loads project-local `.codex/` layers only after you trust the project.

Do not put repository-specific commands, credentials, paths, or security exceptions in your global configuration: they would affect every project. When moving this template to `~/.codex/`, merge the relevant settings with your existing files rather than replacing them wholesale.

## Usage

### Inheritance and precedence

Codex builds an instruction chain when it starts:

1. It loads one global file from `~/.codex`: `AGENTS.override.md` if present, otherwise `AGENTS.md`.
2. It then walks the project from the repository root to the current directory and selects one file per directory: `AGENTS.override.md` first, otherwise `AGENTS.md`.
3. It concatenates the selected files in that order. Instructions closest to the current directory are therefore read last and take precedence only when they conflict; all other instructions remain active.

If your project already has an `AGENTS.md`, **do not replace it**: keep its contents and add this repository's routing instructions to it. To scope instructions to a subdirectory, place another `AGENTS.md` there. Use `AGENTS.override.md` only when you deliberately want Codex to ignore the `AGENTS.md` in the same directory; the two files are not merged.

For configuration, `~/.codex/config.toml` provides user-level values. Each `.codex/config.toml` in a trusted project adds its own values; for the same key, the project layer closest to the current directory wins, while absent keys remain inherited. Command-line options still have higher precedence. Codex ignores local `.codex/` layers until the project is trusted, and some sensitive keys cannot be overridden at project level.

### Installation

Requires Python 3.11 or newer. From this repository, run:

```text
python install.py --global
```

The global layout is `AGENTS.md`, `config.toml`, `agents/`, and `skills/`
directly under `CODEX_HOME` (or `~/.codex` if unset). Use `--dry-run` to
preview every change. The installer preserves existing instructions and
configuration values, backs up modified files under
`CODEX_HOME/.codexskills-backup/`, and warns instead of overwriting divergent
agent or skill files. For an explicit project installation, run
`python install.py path/to/your/project`; omitting the path retains the
current-directory project behavior.

After installation, review any warnings and the model names, approval policy, sandbox mode, and concurrency limit for your environment. Trust the project when Codex asks, then start a new Codex task from that repository so the instruction chain is rebuilt. Project-scoped `.codex/config.toml` is loaded only for trusted projects.

Codex discovers repository instructions from `AGENTS.md`, local skills from `.agents/skills`, and custom agents from `.codex/agents`. See the official documentation for [AGENTS.md](https://developers.openai.com/codex/guides/agents-md), [skills](https://developers.openai.com/codex/skills), [subagents](https://developers.openai.com/codex/subagents), and [configuration](https://developers.openai.com/codex/config-reference).

## Safety boundaries

- Never run with `--yolo` or `--dangerously-bypass-approvals-and-sandbox`.
- Parent runtime permission overrides also apply to spawned agents.
- Do not use `architect` when those overrides would defeat its read-only restrictions.
- `architect` does not explore, execute commands, edit files, or delegate.
- Subagents stay within their assigned role and do not perform routing themselves.

## Customization

Edit `.codex/config.toml` to change the primary model, defaults, or concurrency. Edit the matching file under `.codex/agents/` to change a role. Keep the role boundaries and model names synchronized with `AGENTS.md` and `quota-orchestrator/SKILL.md`.

Model availability depends on your Codex account and environment.
