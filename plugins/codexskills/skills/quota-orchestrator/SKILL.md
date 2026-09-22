---
name: quota-orchestrator
description: Apply automatically at the start of every root task to decide whether work stays local or is delegated. Requires the five complete project profiles installed by quota-orchestrator-setup; strongly prompt for setup when they are missing. Never apply inside an already delegated subagent.
---

# Selective multi-model routing

## Automatic activation

Perform this triage at the beginning of every root task without waiting for the
user to name the skill or plugin. For a small bounded task, keep it at the root
and continue without visible ceremony. Never activate this routing from an
already delegated subagent. Communicate in the user's language.

## Required setup gate

Before routing, verify that all five named agent types are available:
`scout`, `researcher`, `runner`, `builder`, and `architect`.

If any profile is missing:

1. Do not silently claim that full routing is active.
2. Before doing substantial work, prominently tell the user that the plugin is
   installed but its one-time project setup is still required.
3. Ask the user to say, in their language, “Configure the full codexskills
   profiles in this project.” This request activates
   `quota-orchestrator-setup`; no manual TOML editing is required.
4. Keep the current task at the root. Use a reduced built-in fallback only if
   the user explicitly declines or postpones setup. Never emulate `architect`.

Repeat this notice on later root tasks until all five profiles are available.
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

Use the installed `scout`, `researcher`, `runner`, `builder`, and `architect`
profiles. `quota-orchestrator-setup` installs them in the current project with
their complete models, efforts, permissions, and contracts.
The optional `scout_complex` and `researcher_complex` profiles use GPT-6 Sol.
Choose `scout_complex` at triage when contradictory evidence across components
must be resolved; choose `researcher_complex` when contradictory sources affect
an important technical decision. Ordinary missions use GPT-6 Luna. If an
optional profile is unavailable, keep the complex judgment at the root.
These choices are provisional: GPT-5.6 measurements do not prove GPT-6 savings.

If the user explicitly postpones setup, the reduced fallbacks below may be used
for an immediate task. Include the relevant contract directly in the child
prompt and state that guarantees are reduced.

### Scout — `scout`, reduced fallback `explorer`

Read only. Gather the smallest sufficient evidence chain: entry point, relevant
flow, localized cause, paths, and lines. Modify nothing. Stop after three
unsuccessful searches. Report “not found” with what was eliminated instead of
expanding without bound.

### Researcher — `researcher`, reduced fallback `default`, GPT-6 Luna `max`

External research only. Cite URLs, dates, and versions; separate facts from
interpretations; flag contradictions. Five queries maximum. Modify no files
and delegate to nobody.

### Runner — `runner`, reduced fallback `default`, GPT-6 Luna `medium`

Run an already defined validation and report the command, exit code, tested
files, and essential error. Fix only an obvious local mistake. At most three
fix-test cycles, or two for an environment problem. Do not redesign.

### Builder — `builder`, reduced fallback `worker`

Implement an explicit scope with the smallest defensible change. Do not expand
architecture, APIs, schemas, or dependencies without authorization. Validate
the change narrowly. Stop after three attempts and report the decision or
failure.

### Architect — `architect`, no fallback

Rare use: a conceptual decision based on an already assembled context packet.
The installed profile forbids exploration, commands, writes, and delegation.
If it is unavailable or the restrictions cannot be guaranteed in the session,
do not consult Astra. The deliverable contains a diagnosis, recommendation,
alternatives and risks, and required measurements, without a patch.

After the response, verify in the trace the `architect` role, `gpt-6-astra`
model, `low` effort, and absence of tool calls. Without this evidence, discard
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

A run with `Complete = false` is `non observable`: never use its token count or
duration in an economic comparison. Compare at least two complete runs;
otherwise conclude that no economic comparison is possible.

Targeted validation belongs to the agent making the change. Do not request an
independent review by default. A focused review is justified for security, data
loss, an irreversible migration, a public contract, an unresolved
contradiction, or missing reliable tests for critical behavior.

Never widen permissions or use `--yolo` or
`--dangerously-bypass-approvals-and-sandbox` to enable delegation.
