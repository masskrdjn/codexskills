# Selective Multi-Model Routing for Codex

[Français](README.fr.md)

A project-scoped Codex configuration that routes work to specialized agents only when delegation is likely to preserve quality while reducing total cost or latency. The primary agent remains responsible for decisions, integration, and user communication.

## Routing policy

Priorities, in order:

1. Preserve result quality and relevance.
2. Reduce total cost, including coordination and rework.
3. Reduce latency.

Small, bounded tasks stay with the primary agent. Delegation is used when a clearly scoped role can perform substantial work more efficiently or provide useful independent analysis.

| Role | Model | Effort | Responsibility |
| --- | --- | --- | --- |
| Primary | `gpt-5.6-sol` | `medium` | Triage, decisions, integration, and small local tasks |
| `scout` | `gpt-5.6-luna` | `max` | Read-only codebase and log exploration |
| `researcher` | `gpt-5.6-luna` | `max` | Multi-source external research |
| `runner` | `gpt-5.6-luna` | `medium` | Long validations and large mechanical batches |
| `builder` | `gpt-5.6-terra` | `high` | Scoped implementation with targeted validation |
| `architect` | `gpt-6-astra` | `low` | Rare, bounded architecture decisions only |

The default subagent is Luna at `max` effort. Concurrency is capped at four spawned threads per session.

## Project layout

```text
.
├── AGENTS.md
├── .agents/skills/quota-orchestrator/SKILL.md
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

## Installation

Clone the repository into a directory you want to use as a Codex project:

```bash
git clone https://github.com/masskrdjn/codexskills.git
cd codexskills
```

Alternatively, copy or merge `AGENTS.md`, `.agents/`, and `.codex/` into the root of an existing repository, then review the configuration for that project before trusting it in Codex.

## Usage

1. Review the model names, approval policy, sandbox mode, and concurrency limit for your environment.
2. Trust the project when Codex asks; project-scoped `.codex/config.toml` is loaded only for trusted projects.
3. Start a new Codex task from that repository.
4. Ask Codex to summarize its active instructions if you want to verify discovery.

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

