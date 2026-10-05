# Selective Multi-Model Routing for Codex

[Français](README.fr.md)

A Codex configuration template that routes work to specialized agents only when delegation is likely to preserve quality while reducing total cost or latency. The primary agent remains responsible for decisions, integration, and user communication.

## Routing policy

Priorities, in order:

1. Preserve result quality and relevance.
2. Reduce total cost in API dollars (tokens of each type times the model's rate, so more tokens on a cheaper tier is a good trade at equal quality), including coordination and rework.
3. Reduce latency.

Small, bounded tasks stay with the primary agent. Delegation is used when a clearly scoped role can perform substantial work more efficiently or provide useful independent analysis.

## Compare models independently of roles

Roles define missions, restrictions, and deliverables. They do not rank models
or effort levels. Compare all five models for the task; this project establishes
no universal ranking of quality or token consumption.

| Model | Project candidacy | Boundary to preserve |
|---|---|---|
| GPT-6 Luna | Bounded work; `high`, `xhigh`, and `max` are candidates, including well-defined implementation or framing | User floor `high` in named roles and the generic agent. About 20x cheaper than Sol 6.1 per token: see the cost rule. |
| GPT-6 Sol | Ordinary candidate for technical missions and complex interactions, independently of role | Same quality gate and comparison protocol as Sol 6.1, no proof tied to its age; same rates as 6.1 except cached input, 2x more expensive. |
| GPT-5.6 Sol | Ordinary candidate for reasoning, framing, and other missions it can fulfill | Same requirements as other Sol models; no compatibility-only exception or presumed inferiority; rate is 2x that of 6.1 (promotional, see the cost rule). |
| GPT-6.1 Sol | Candidate across implementation, research, and decisions | Being newer establishes neither fewer tokens nor an optimal replacement for other Sol models. |
| GPT-6 Astra | An `architect` consultation when extra capacity addresses an identified difficulty | Preserve quota and architect restrictions: no exploration, commands, writing, or delegation. 5x the 6.1 rate (10x cached), 100x Luna. |

Verify the models and efforts actually available in the runtime. API support
does not establish Codex availability. Effort names are not equivalent across
models: Luna `xhigh` does not mean Sol `medium`, nor Sol `xhigh` Astra `low`.

## Choose capacity, then cost

Choose model and effort from contract ambiguity, dependencies and interactions,
contradictions, validation difficulty, and consequences of error. Batch length,
file count, and role names are insufficient. Missing evidence needs targeted
collection, not automatically more effort. This assessment does not authorize
exploration before the routing decision.

1. **Capacity**: identify admissible combinations that can meet the same quality
   and relevance criteria, with validation appropriate to the consequences of
   error. Exclude a combination for an identified limit, not its age; price
   enters the cost, not admissibility. Keep decisive uncertainty explicit.
2. **Cost**: among admissible combinations, compare whole-job cost (rates
   below), including root, children, and reviewers, then latency. Tokens are
   reported without arbitrating. Without comparable measurements, the choice
   remains a policy hypothesis, not demonstrated savings or an optimum.

The grid proposes candidates to evaluate. Each Sol means GPT-6 Sol, GPT-5.6
Sol, and GPT-6.1 Sol under the same admission criteria. Proposed efforts remain
conditional on their actual availability.

| Task difficulty and evidence | Candidate combinations | Validation and reclassification trigger |
|---|---|---|
| Explicit contract, little ambiguity, direct validation | Luna `high`; each Sol `low`/`medium` | Direct acceptance checks. Small tasks stay at the root by default. |
| Multiple constrained steps, limited judgment | Luna `high`/`xhigh`; each Sol `medium`/`high` | Check interactions between steps; report decisive ambiguity. |
| Nontrivial interactions, subtle invariants, competing hypotheses | Luna `high`/`xhigh`/`max` if capacity is admissible; each Sol `medium`/`high`/`xhigh` | Validate invariants and distinguish hypotheses; change model when capacity is the limiting factor. |
| Contradictory evidence, difficult synthesis, indirect validation | Each Sol `high`/`xhigh`/`max`; Luna `xhigh`/`max` if capacity is admissible | Preserve caveats; reclassify persistent decisive contradictions. |
| Structural decision, expensive correction, persistent ambiguity | Each Sol `high`/`xhigh`/`max`; Astra consultation at a suitable available effort | Justify additional capacity and preserve the architect context boundary. |

`xhigh` and `max` are candidates to compare, not automatic promotions. Neither
a researcher role nor low pricing selects `max` automatically. Evaluating `max`
does not require exhausting all lower efforts first: justify candidacy from
the task, then measure quality and whole-job cost. Luna fallbacks are `high`,
including runner and generic; this provisional policy respects the user floor
without establishing that `high` is optimal. Existing fallback models stay in
place; TOML values and successful execution do not prove savings. The optional
scout_complex and researcher_complex profiles are runtime conveniences, not a
mandatory ranking: the standard variant (Luna) is the default; the complex one
(Sol 6.1 xhigh, 20x per token and longer reasoning) requires capacity
established at framing or an observed limit of the standard variant.

At launch, record role, exact model, effort, supporting facts, hypotheses,
unknowns, expected validation, and reclassification trigger. Use explicit
overrides and `fork_turns = "none"` only where supported. If the runtime locks
the profile, choose an available profile preserving its contract and restrictions;
otherwise retain the task at the root and disclose the unsupported combination.
A generic fits only if those guarantees can be preserved. Prompt instructions
do not replace disabled tools. Never claim an unapplied override. An Astra
subagent consultation uses a verifiable architect profile exclusively. Preserve
the user's primary model and effort; the Luna floor applies to subagent
selections.

The child reports facts invalidating the initial selection; only the root
reclassifies. Execution difficulty does not automatically justify more capacity.
Reuse relevant evidence and validation instead of repeating work. Report a
decisive conceptual difficulty immediately.

### API prices and cost rule

Standard rates (input <= 272K tokens), dollars per million tokens, retrieved
2026-10-03 from https://developers.openai.com/api/docs/pricing (the page carries
no version: refresh before comparing runs dated otherwise).

| Model | Input | Cached input | Cache write | Output (reasoning included) | Output vs Luna |
|---|---|---|---|---|---|
| GPT-6 Luna | 0.10 | 0.01 | 0.125 | 0.50 | 1x |
| GPT-6 Sol | 2.00 | 0.20 | 2.50 | 10.00 | 20x |
| GPT-6.1 Sol | 2.00 | 0.10 | 2.50 | 10.00 | 20x |
| GPT-5.6 Sol | 4.00 | 0.40 | 5.00 | 20.00 | 40x |
| GPT-6 Astra | 10.00 | 1.00 | 12.50 | 50.00 | 100x |

GPT-5.6 Sol's rate is promotional at least through November 21, 2026. Above 272K
input tokens a request pays input, cached input, and cache writes at 2x and
output at 1.5x for the whole request. Fast is 2x, Batch and Flex 0.5x (Ultrafast
6x, Astra only): compare at the same service tier, since logs do not record it.
An input token is billed as uncached, cached, or cache write, never cumulatively.

Cost rule: at equal admissible capacity, compare the sum of tokens x rate, not
tokens. Luna stays cheaper than Sol 6.1 while it consumes fewer than 20x (input,
output) or 10x (cached) the tokens. Trying a cheaper tier first pays off when
cost_low + (1 - p) x cost_high < cost_high, that is p > cost_low / cost_high,
where p is the probability that the low tier suffices and that its insufficiency
is detected before delivery: without verifiable criteria (return contract), an
undetected error cannot be recovered and this calculation does not apply.
Escalate on an identified capacity limit, not as a precaution. Sol 6 (cached 2x)
and Sol 5.6 (2x the 6.1 rate, 4x cached) win only through measured lower
consumption: under half the 6.1 tokens for 5.6, at equal quality. Keeping the
root context under 272K is a benefit of delegation; a full fork to another model
restarts without cache and may cross the threshold. Astra remains a quota
constraint on top of cost.

### Official sources and limits

Research supplied by the root, consulted September 29, 2026:
[selection](https://developers.openai.com/api/docs/guides/model-selection),
[migration](https://developers.openai.com/api/docs/guides/latest-model),
[Luna](https://developers.openai.com/api/docs/models/gpt-6-luna),
[Sol 6](https://developers.openai.com/api/docs/models/gpt-6-sol),
[Sol 5.6](https://developers.openai.com/api/docs/models/gpt-5.6-sol),
[Sol 6.1](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).
The model pages position Luna for narrow work, Sol 6.1 for complex work, and
Astra for demanding tasks. The selection guide recommends testing candidates
on the same inputs and retaining a setting that meets the quality bar. Sol 6
pointing to 6.1 does not establish fewer tokens in this repository. API prices
ground the cost calculation; neither they nor external evaluations demonstrate
project savings, which remain to be measured. The Luna high floor is a user preference separate from documentation examples. The
grid remains a hypothesis to validate, not a comparative recommendation proven
by these sources.

## Measure cost without conflating tokens, price, and quality

This revision measures no savings. A comparison requires
the same tasks, acceptance criteria, supplied context, tools and permissions,
validation, and attempt budget. Identify every run, task, scenario, effective
model/effort, arm, and repetition; pair runs and randomize candidate order.
Publish cold-cache and warm-cache results separately. Two unpaired complete
runs cannot support an economic conclusion. Exploratory comparisons require
at least two complete pairs per task/scenario; this does not replace the
existing five complete comparable randomized pairs needed to promote a local
task to cost-driven delegation on cold-cache evidence.

Count the whole job: input context, reasoning, responses, tool exchanges,
framing, coordination, integration, validation, corrections, and rework,
including root, children, and reviewers. Tool calls contribute their model
exchange tokens; do not add their text again to usage counters. When `Reasoning`
is included in `Output`, total is `Input + Output`, not `Input + Output + Reasoning`.
When `Cached` is included in `Input`, do not add it again; distinguish
`Uncached = Input - Cached`. Cache writes are a third input type, billed apart.
Verify these inclusions in the counter source.

The criterion is API dollars per accepted result: the sum over responses of
tokens of each type times the model's dated rate (long-context and service-tier
multipliers included), successes, failures, and reruns included; per complete
run when no quality verdict exists. Report total and component tokens, latency,
quality, and success rate separately. Codex credits are not API dollars: the API
rate is a proxy for a subscription, and the Astra quota remains a separate
constraint. Include complete successes and failures, corrections, and reruns under
a rule fixed before execution; do not compare survivors alone. A complete
failure remains observable. A run with `Complete = false` is exactly
`non observable`: exclude its tokens and duration from all ratios, medians, and
economic recommendations; retain its diagnostic and the incomplete-run count.
Do not create a pair from a surviving run; insufficient admissible pairs mean
no economic conclusion. Measure `guardian_review` separately and include it in
the total without describing it as directly controllable. Publish limits of
representativeness.

## Fallback profiles

These values are fallbacks when the runtime cannot apply an explicit selection. They do not replace the per-task grid or demonstrate optimality. The generic
subagent also uses Luna `high`. Customized installed settings remain preserved
with warnings; review them explicitly if they conflict with the Luna floor.

| Role | Fallback model | Fallback effort | Responsibility |
| --- | --- | --- | --- |
| Primary | User-selected | Variable | Triage, decisions, integration, and small local tasks |
| `scout` | `gpt-6-luna` | `high` | Read-only codebase and log exploration |
| `scout_complex` (optional) | `gpt-6.1-sol` | `xhigh` | Complex causal investigation or review once Sol-level capacity is established (`scout` is the default) |
| `researcher` | `gpt-6-luna` | `high` | Multi-source external research |
| `researcher_complex` (optional) | `gpt-6.1-sol` | `xhigh` | Synthesize conflicting sources for an important technical decision (`researcher` is the default) |
| `runner` | `gpt-6-luna` | `high` | Long validations and large mechanical batches |
| `builder` | `gpt-6.1-sol` | `high` | Substantial implementation with targeted validation |
| `strategist` | `gpt-6.1-sol` | `medium` | Complex framing, decomposition, and intermediate tradeoffs |
| `architect` | `gpt-6-astra` | `low` | Rare, bounded architecture decisions only |

## Project layout

```text
.
├── AGENTS.md
├── .agents/skills/quota-orchestrator/SKILL.md
├── .agents/plugins/marketplace.json
├── plugins/codexskills/
│   ├── .codex-plugin/plugin.json
│   ├── hooks/hooks.json, hooks/reconcile.py
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
        ├── researcher_complex.toml
        ├── runner.toml
        ├── scout.toml
        ├── scout_complex.toml
        └── strategist.toml
```

- `AGENTS.md` defines the repository-wide routing and safety rules.
- `quota-orchestrator` decides whether delegation is worth its full cost.
- `.codex/config.toml` selects the primary model and enables multi-agent work.
- `.codex/agents/*.toml` defines each role's model, tools, limits, and reporting contract.
- `.agents/plugins/marketplace.json` exposes the repository's Codex catalog.
- `plugins/codexskills/` contains the manifest, both skills, the controlled installer, and the complete profiles distributed as templates.
- The measurement tooling behind the numbers quoted below (dated price table, per-response usage exporter, paired-run harness) is local and not versioned. `fixtures/release_0_8_0/` keeps the authentic 0.8.0 files that the installer tests migrate from.

## Install as a plugin

> [!IMPORTANT]
> Current plugin version: **0.8.2**.
>
> An approved repository marketplace installs the plugin by default. Codex
> still asks you to trust its bundled SessionStart hook once. That hook then
> configures the six global profiles and checks them on later sessions.

From the local checkout, to test before publishing:

```text
codex plugin marketplace add .
```

After publishing the repository:

```text
codex plugin marketplace add masskrdjn/codexskills
```

When Codex prompts you to review the bundled hook, trust it once if you want
automatic setup. At SessionStart it runs a local Python 3.11+ script, without
network access or marketplace upgrades. The script installs and later
reconciles `scout`, `researcher`, `runner`, `builder`, `strategist`, and
`architect` in `CODEX_HOME` (or `~/.codex` when unset). It merges compatible
settings, backs up modified files under `CODEX_HOME/.codexskills-backup/`, and
preserves divergent files with an actionable warning. State and a short-lived
concurrency lock live in `PLUGIN_DATA`, or `CODEX_HOME/.codexskills-data` if
the runtime does not provide it. A failure only defers reconciliation to the
next session. Start a new Codex task to load newly installed profiles.

If the hook is declined, unavailable, or warns about a conflict, ask Codex to
"Configure the full codexskills profiles" for a manual preview and recovery.
The marketplace's default-install policy does not bypass project, plugin, or
hook trust. Updating the marketplace package is separate: the hook applies
only the version already installed and never fetches a newer one. On systems
without a `python` command resolving to Python 3.11+, use the manual setup or
make that interpreter available before trusting the hook.

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

### Manual installation and recovery

This path is only for installation without the plugin, recovery after declining
the hook, or explicit testing of the installer. Normal plugin users do not need
to run this command. It requires Python 3.11 or newer:

```text
python install.py --global
```

The global layout is `AGENTS.md`, `config.toml`, `agents/`, and `skills/`
directly under `CODEX_HOME` (or `~/.codex` if unset). Use `--dry-run` to
preview every change. The installer upgrades exact matches to previously
distributed files, backs up modified files under
`CODEX_HOME/.codexskills-backup/`, and preserves customized files and
configuration values with warnings. For an explicit project installation, run
`python install.py path/to/your/project`; omitting the path retains the
current-directory project behavior.
To migrate an existing generic subagent default from GPT-5.6 Luna to GPT-6
Luna, pass `--upgrade-default-model` to both the dry run and install command.

After installation, review any warnings and the model names, approval policy, sandbox mode, and concurrency limit for your environment. Trust the project when Codex asks, then start a new Codex task from that repository so the instruction chain is rebuilt. Project-scoped `.codex/config.toml` is loaded only for trusted projects.

Codex discovers repository instructions from `AGENTS.md`, local skills from `.agents/skills`, and custom agents from `.codex/agents`. See the official documentation for [AGENTS.md](https://developers.openai.com/codex/guides/agents-md), [skills](https://developers.openai.com/codex/skills), [subagents](https://developers.openai.com/codex/subagents), and [configuration](https://developers.openai.com/codex/config-reference).

## Safety boundaries

- Never run with `--yolo` or `--dangerously-bypass-approvals-and-sandbox`.
- Parent runtime permission overrides also apply to spawned agents.
- Do not use `architect` when those overrides would defeat its read-only restrictions.
- `strategist` prepares the plan but never spawns subagents itself.
- `architect` does not explore, execute commands, edit files, or delegate.
- Subagents stay within their assigned role and do not perform routing themselves.

## Customization

Edit `.codex/config.toml` to change the primary model, defaults, or concurrency. Edit the matching file under `.codex/agents/` to change a role. Keep the role boundaries and model names synchronized with `AGENTS.md` and `quota-orchestrator/SKILL.md`.

Model availability depends on your Codex account and environment.

## Measured overhead and the lean hot path

A first paired benchmark (15 runs, Astra root, cold cache, run with a local
harness that is not versioned) showed that the previous routing cost more than the root
alone on every task of that size. Reading a 32 KB skill at the start of every task
(its description said "apply automatically") plus an 11 KB `AGENTS.md` added about
$0.2 per run: the run that only executes the test suite cost $0.12 alone and
$0.33 routed. Every coordination request (spawn, wait, list, message) re-reads
about 30K cached tokens at the root's rate, while the scout itself cost under
$0.01 (Luna): the bill is the root's. These are single-repetition observations,
not a demonstrated result.

The routing path was therefore reduced, and the effect is predicted, not yet
measured:

- `AGENTS.md` (about 5 KB) carries everything everyday triage and standard
  delegation need: what stays at the root, when `scout`, `researcher`, `runner`
  or `builder` apply, a short handoff, a single long `wait_agent`, and targeted
  acceptance reads (a wider re-read is a redo and cancels the substitution).
- The skill is read on demand only: model or effort outside the profiles,
  `_complex` variants, `strategist`, `architect`, independent review, cost
  measurement, or a missing profile. Its description no longer says
  "automatically" or "every task", and `AGENTS.md` stays under 6 KB because it
  is paid on every request of every agent.
- A `scout` is worth its coordination only for a wide exploration (about eight
  files or 60 KB; measured to pay for an exhaustive read-only audit: 34 %, 41 %
  and 42 % cheaper at 8, 16 and 48 files, with a latency 2.5 to 3.5 times
  longer); smaller reviews and traces stay at the root.
- Waiting for a child is configured, not only requested. A wide audit run (T6) showed the root
  polling with `wait_agent` every 60 seconds, four times, although the instruction asked for one
  long wait: each poll is a full root request, together a quarter of the root's cost. `config.toml`
  now carries `[features.multi_agent_v2]` with a five-minute floor (`min_wait_timeout_ms` and
  `default_wait_timeout_ms` at 300000, `max_wait_timeout_ms` at 3600000), and `AGENTS.md` names the
  value. `wait_agent` still returns as soon as the child answers, so the floor removes polls, not
  progress. Codex refuses to load a configuration unless `min <= default <= max`, so the installer
  adds the three keys only as a group, only when the user has none of them, and never when the user
  already defines `multi_agent_v2` another way (a boolean flag, an inline table); it then says why.
- Scout and researcher reports are capped at about 400 words, because they enter
  the root's context at the root's rate. Review mode also checks edge cases (empty
  input, `None` or zero, bounds, division, swallowed errors) after both delegated
  reviews of the benchmark missed an empty-list defect that the root alone found.

## 0.8.1 contracts and distribution

Cost is the criterion: API dollars per accepted result, computed per response
from the dated API prices (cache, cache writes, the long-context surcharge above 272K
input tokens, and the service tier). More tokens on a cheaper tier is a good
trade; a candidate that costs less passes the measurement gate even if it uses
more tokens. Keep the price tables in both skills and both READMEs equal to
each other and to the dated prices they cite.

Delegation transfers execution, not responsibility for closure. Each criterion
returns verified, failed, or not verified, with evidence and analyzed state;
the root reconciles the results, examines the final diff and performs necessary
acceptance checks. Builder/runner require test-runner completion evidence in
addition to exit code; code 0 alone means validation not established. Scout
distinguishes causal investigation (the default) from review of all assigned
axes. Architect restrictions apply to the consultant, not a user-selected Astra
root; announced model, configuration and attested execution are distinct.
Independent review remains conditional, with an explicit root decision when a
listed risk is affected.

Distribution reference: `plugins/codexskills/templates/AGENTS.md`,
`templates/.codex/config.toml`, `templates/.codex/agents/*.toml`, and
`templates/.agents/skills/quota-orchestrator/SKILL.md` (under `plugins/codexskills/`).
Update their root copies together with the English skill and fallbacks in
`plugins/codexskills/skills/quota-orchestrator/SKILL.md`, both installers
`install.py` and `plugins/codexskills/scripts/install.py`, the plugin manifest,
and French/English READMEs. Local copies and templates must match after
line-ending normalization.

Authentic 0.8.0 contents, raw and normalized fingerprints, and the managed
AGENTS block are preserved in `fixtures/release_0_8_0/`. Official profiles migrate
with backups; customizations remain intact with warnings. Update the installed
package, then open a new task. SessionStart reconciles only that installed
package, without downloads or runtime mission validation. Plugin consistency
is tested; model compliance with the contracts is not automatically guaranteed.
