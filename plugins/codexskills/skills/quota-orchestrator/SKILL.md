---
name: quota-orchestrator
description: Apply automatically at the start of every root task to decide whether work stays local or is delegated. Requires the six complete project profiles installed by quota-orchestrator-setup; strongly prompt for setup when they are missing. Never apply inside an already delegated subagent.
---

# Selective multi-model routing

## Automatic activation

Perform this triage at the beginning of every root task without waiting for the
user to name the skill or plugin. For a small bounded task, keep it at the root
and continue without visible ceremony. Never activate this routing from an
already delegated subagent. Communicate in the user's language.

## Required setup gate

Before routing, verify that all six named agent types are available:
`scout`, `researcher`, `runner`, `builder`, `strategist`, and `architect`.

If any profile is missing:

1. Do not silently claim that full routing is active.
2. Before doing substantial work, prominently tell the user that the plugin is
   installed but its one-time project setup is still required.
3. Ask the user to say, in their language, “Configure the full codexskills
   profiles in this project.” This request activates
   `quota-orchestrator-setup`; no manual TOML editing is required.
4. Keep the current task at the root. Use a reduced built-in fallback only if
   the user explicitly declines or postpones setup. Never emulate `architect`.

Repeat this notice on later root tasks until all six profiles are available.
After setup, tell the user to start a new Codex task so the profiles are loaded.

## Objective

Preserve quality and relevance first, then reduce total cost, then latency.
Compare the whole job: framing, context, execution, waiting, integration,
validation, and possible rework. Without comparable measurements, describe an
expected benefit, never a demonstrated saving.

This skill is for the root agent only. An assigned child follows its mission;
it does not reload this skill, repeat triage, or delegate again.

## Decide before exploring

A bounded triage may inventory relevant files or symbols. It must not trace
callers, open multiple implementations, or test causal hypotheses before the
routing decision.

| Situation | Route after setup |
|---|---|
| Small local task, direct read, or bounded deterministic batch | Root |
| Unknown entry point, cross-component flow, or competing causal hypotheses | `scout` |
| External research with multiple questions or sources | `researcher` |
| Long independent validation | `runner` |
| Substantial bounded implementation | `builder` |
| Complex framing, decomposition, or intermediate tradeoff on assembled context | `strategist` |
| Exceptional conceptual decision | `architect` |

A one-off lookup using one source stays at the root. As soon as a second query,
source, or question is needed, create the researcher before continuing.

Create the scout immediately when the entry point must be discovered, callers,
data, or state must be traced across components, or competing hypotheses must
be resolved.

## Substitution gate

A cost-driven delegation must replace root work, not merely add another
executor. Before spawning a child, briefly state:

1. its exclusive deliverable;
2. the work the root will stop doing;
3. the verifiable stopping condition;
4. why the expected benefit covers coordination cost.

Without concrete answers to all four, keep the work at the root. After the
result returns, integrate it without repeating the exploration. A targeted
verification of one piece of evidence is allowed.

The delegated scope belongs exclusively to the child until it responds. The
root may wait, work on a disjoint scope announced before launch, or ask a
question whose answer cannot change the delegated work. If the root can already
conclude, interrupt the child instead of duplicating the work.

## Complete profiles and reduced fallback

Use the installed `scout`, `researcher`, `runner`, `builder`, `strategist`, and `architect`
profiles. `quota-orchestrator-setup` installs them in the current project with
their fallback settings and complete contracts. Effective permissions remain
subject to the parent runtime, which takes precedence over child sandbox defaults.
## Compare models independently of roles

Roles define missions, restrictions, and deliverables. They do not rank models
or effort levels. Compare all five models for the task; this project establishes
no universal ranking of quality or token consumption.

| Model | Project candidacy | Boundary to preserve |
|---|---|---|
| GPT-6 Luna | Bounded work; `high`, `xhigh`, and `max` are candidates, including well-defined implementation or framing | User floor `high` in named roles and the generic agent. A low token price does not establish lower token consumption. |
| GPT-6 Sol | Ordinary candidate for technical missions and complex interactions, independently of role | Same quality gate and comparison protocol as Sol 6.1; no extra proof required because of its age. |
| GPT-5.6 Sol | Ordinary candidate for reasoning, framing, and other missions it can fulfill | Same requirements as other Sol models; no compatibility-only exception or presumed inferiority. |
| GPT-6.1 Sol | Candidate across implementation, research, and decisions | Being newer establishes neither fewer tokens nor an optimal replacement for other Sol models. |
| GPT-6 Astra | An `architect` consultation when extra capacity addresses an identified difficulty | Preserve quota and architect restrictions: no exploration, commands, writing, or delegation. |

Verify the models and efforts actually available in the runtime. API support
does not establish Codex availability. Effort names are not equivalent across
models: Luna `xhigh` does not mean Sol `medium`, nor Sol `xhigh` Astra `low`.

## Choose capacity, then token efficiency

Choose model and effort from contract ambiguity, dependencies and interactions,
contradictions, validation difficulty, and consequences of error. Batch length,
file count, and role names are insufficient. Missing evidence needs targeted
collection, not automatically more effort. This assessment does not authorize
exploration before the routing decision.

1. **Capacity**: identify admissible combinations that can meet the same quality
   and relevance criteria, with validation appropriate to the consequences of
   error. Exclude a combination for an identified limit, not its age or price.
   Keep decisive uncertainty explicit.
2. **Efficiency**: among admissible combinations, compare whole-job tokens,
   including root, children, and reviewers, then monetary cost and latency
   separately. Without comparable measurements, the choice remains a policy
   hypothesis, not demonstrated savings or an optimum.

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
the task, then measure quality and whole-job tokens. Luna fallbacks are `high`,
including runner and generic; this provisional policy respects the user floor
without establishing that `high` is optimal. Existing fallback models stay in
place; TOML values and successful execution do not prove savings. The optional
scout_complex and researcher_complex profiles are runtime conveniences, not a
mandatory ranking.

At launch, record role, exact model, effort, supporting facts, hypotheses,
unknowns, expected validation, and reclassification trigger. Use explicit
overrides and `fork_turns = "none"` only where supported. If the runtime locks
the profile, choose an available profile preserving its contract and restrictions;
otherwise retain the task at the root and disclose the unsupported combination.
A generic fits only if those guarantees can be preserved. Prompt instructions
do not replace disabled tools. Never claim an unapplied override. Astra uses
a verifiable architect profile exclusively. Preserve the user's primary model
and effort; the Luna floor applies to subagent selections.

The child reports facts invalidating the initial selection; only the root
reclassifies. Execution difficulty does not automatically justify more capacity.
Reuse relevant evidence and validation instead of repeating work. Report a
decisive conceptual difficulty immediately.

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
and external evaluations do not demonstrate project token savings. The Luna
high floor is a user preference separate from documentation examples. The
grid remains a hypothesis to validate, not a comparative recommendation proven
by these sources.

## Measure tokens, price, and quality separately

This revision measures no savings or token reduction. A comparison requires
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
`Uncached = Input - Cached`. Verify these inclusions in the counter source.

Report total and component tokens, monetary cost using dated model-specific
rates, latency, quality, and success rate separately. Codex credits are not API
dollars. Include complete successes and failures, corrections, and reruns under
a rule fixed before execution; do not compare survivors alone. A complete
failure remains observable. A run with `Complete = false` is exactly
`non observable`: exclude its tokens and duration from all ratios, medians, and
economic recommendations; retain its diagnostic and the incomplete-run count.
Do not create a pair from a surviving run; insufficient admissible pairs mean
no economic conclusion. Measure `guardian_review` separately and include it in
the total without describing it as directly controllable. Publish limits of
representativeness.

If the user explicitly postpones setup, the reduced fallbacks below may be used
for an immediate task. Include the relevant contract directly in the child
prompt and state that guarantees are reduced.

### Scout — `scout`, reduced fallback `explorer`

Read only. Gather the smallest sufficient evidence chain: entry point, relevant
flow, localized cause, paths, and lines. Modify nothing. Stop after three
unsuccessful searches. Report “not found” with what was eliminated instead of
expanding without bound.

### Researcher — `researcher`, reduced fallback `default` with task-selected model/effort

External research only. Cite URLs, dates, and versions; separate facts from
interpretations; flag contradictions. Five queries maximum. Modify no files
and delegate to nobody.

### Runner — `runner`, reduced fallback `default` with task-selected model/effort

Run an already defined validation and report the command, exit code, tested
files, and essential error. Fix only an obvious local mistake. At most three
fix-test cycles, or two for an environment problem. Do not redesign.

### Builder — `builder`, reduced fallback `worker`

Implement an explicit scope with the smallest defensible change. Do not expand
architecture, APIs, schemas, or dependencies without authorization. Validate
the change narrowly. Stop after three attempts and report the decision or
failure.

### Strategist — `strategist`, no fallback

Read only and context bound. Turn already assembled evidence into a decision,
decomposition, execution order, role assignments, contracts, and acceptance
criteria. Do not explore, execute commands, write files, or spawn agents. The
primary agent performs the actual orchestration. Do not insert this role before
an implementation whose contract is already explicit, and do not escalate to
Astra when a targeted measurement can settle the question.

### Architect — `architect`, no fallback

Rare use: a conceptual decision based on an already assembled context packet.
The installed profile forbids exploration, commands, writes, and delegation.
If it is unavailable or the restrictions cannot be guaranteed in the session,
do not consult Astra. The deliverable contains a diagnosis, recommendation,
alternatives and risks, and required measurements, without a patch.

After the response, verify in the trace the `architect` role, `gpt-6-astra`
model, the announced effort, and absence of tool calls. Without this evidence, discard
the result and do not claim that Astra was consulted.

## Handoff

Use `fork_turns = "none"` unless complete history is explicitly necessary. The
self-contained message includes the objective, acceptance criteria, scope,
constraints, established facts, hypotheses, unknowns, completed validations,
and expected result format. State that the child must not reload this skill or
delegate.

Do not turn a hypothesis into a fact in the synthesis. Preserve caveats,
conditional alternatives, and measurements still needed.

## Measurement and validation

Apply the paired measurement protocol above. A run with `Complete = false`
is exactly `non observable`; never use its tokens or duration in economic
comparisons. Complete failures remain observable and must be included.

Targeted validation belongs to the agent making the change. Do not request an
independent review by default. A focused review is justified for security, data
loss, an irreversible migration, a public contract, an unresolved
contradiction, or missing reliable tests for critical behavior.

Never widen permissions or use `--yolo` or
`--dangerously-bypass-approvals-and-sandbox` to enable delegation.
