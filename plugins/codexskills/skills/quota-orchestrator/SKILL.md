---
name: quota-orchestrator
description: Protocol for choosing a model or effort outside the profiles, a _complex variant, strategist, an architect consultation, an independent review, or a cost measurement. Do not read it for a local task or to delegate to a standard scout, researcher, runner, builder_luna, or builder: AGENTS.md is enough. Also read it when the nine named agent types (scout, researcher, runner, builder_luna, builder, visual_operator, writer, strategist, architect) are unavailable, to guide the one-time quota-orchestrator-setup. Never apply inside an already delegated subagent.
---

# Selective multi-model routing

## Activation

Everyday triage and delegation to a standard profile are described in AGENTS.md,
which the host loads: do not read this skill for them. Read it only for a choice
of model or effort outside the profiles, a `_complex` variant, `strategist`, an
`architect` consultation, an independent review, a cost measurement or
comparison, a missing profile, or a situation AGENTS.md does not settle. Each
read costs thousands of input tokens that every later request re-reads. Never
activate it from an already delegated subagent. Communicate in the user's language.

## Required setup gate

When this skill is read for routing, verify that all nine named agent types are available:
`scout`, `researcher`, `runner`, `builder_luna`, `builder`, `visual_operator`, `writer`, `strategist`, and `architect`.

If any profile is missing:

1. Do not silently claim that full routing is active.
2. Before doing substantial work, prominently tell the user that the plugin is
   installed but its one-time project setup is still required.
3. Ask the user to say, in their language, “Configure the full codexskills
   profiles in this project.” This request activates
   `quota-orchestrator-setup`; no manual TOML editing is required.
4. Keep the current task at the root. Use a reduced built-in fallback only if
   the user explicitly declines or postpones setup. Never emulate `architect`.

Repeat this notice on later root tasks until all nine profiles are available.
After setup, tell the user to start a new Codex task so the profiles are loaded.

## Objective

Preserve quality and relevance first, then reduce total cost, then latency.
Cost means API dollars: for every response, tokens of each type (uncached input,
cached input, cache writes, output including reasoning) times the model's API
rate, root, children, and reviewers included. More tokens on a cheaper tier is a
good trade while quality holds; token count is not the criterion. Compare the
whole job: framing, context, execution, waiting, integration, validation, and
possible rework. Without comparable measurements, describe an expected benefit,
never a demonstrated saving.

This skill is for the root agent only. An assigned child follows its mission;
it does not reload this skill, repeat triage, or delegate again.

## Decide before exploring

A bounded triage may inventory relevant files or symbols. It must not trace
callers, open multiple implementations, or test causal hypotheses before the
routing decision.

Before spawning any child, compare its model and reasoning effort, as set by
the profile, applied overrides, or inheritance, with the primary agent's.
If both values are identical, keep the work at the root. This rule takes
precedence over every route below, including `researcher`, `_complex` variants,
capacity, quality, or latency needs, and independent reviews. A different role
is insufficient; do not artificially change the model or effort to bypass
this rule.

| Situation | Route after setup |
|---|---|
| Small local task, direct read, or bounded deterministic batch | Root |
| Unknown entry point, cross-component flow, or competing causal hypotheses, with an exploration wide enough to exceed coordination (about nine files or 60 KB; measured to pay for a read-only audit) | `scout`; otherwise root |
| Bounded review wide enough (several axes, same threshold) to amortize coordination | `scout` in bounded-review mode; otherwise root |
| External research with multiple questions or sources | `researcher` |
| Long independent validation | `runner` |
| Fully specified substantial implementation with reliable targeted validation | `builder_luna` (Luna Max) |
| Implementation requiring design, tradeoffs, or integration | `builder` |
| Substantial visual mission with an action budget, observable stop, and suitable tools | `visual_operator` (Terra 6.1 `medium`); connectors/APIs first |
| Substantial drafting or rewriting from established facts, with audience and acceptance criteria | `writer` (Terra 6.1 `medium`); small edits stay at the root |
| Complex framing, decomposition, or intermediate tradeoff on assembled context | `strategist` |
| Exceptional conceptual decision | `architect` |

A one-off lookup using one source stays at the root. As soon as a second query,
source, or question is needed, create the researcher before continuing if its
model/effort pair differs from the root's; otherwise do the research at the root.

Create the scout immediately when, beyond the exploration threshold above, the
entry point must be discovered, callers, data, or state must be traced across
components, or competing hypotheses must be resolved. Below the threshold,
coordination costs more than the exploration and the root keeps it. Assign the mode (causal investigation by default, or bounded
review) and choose `scout` (Luna); `scout_complex` only under the cost rule.

## Substitution gate

A cost-driven delegation must replace root work, not merely add another
executor. Before spawning a child, briefly state:

1. its exclusive deliverable;
2. the work the root will stop doing;
3. the verifiable stopping condition;
4. why the expected benefit covers coordination cost.

Without concrete answers to all four, keep the work at the root. After the
result returns, integrate it without repeating the exploration. Reading the
result and the diff and running the targeted checks necessary for acceptance is
allowed: these are input tokens, far cheaper than producing the work. Only a redo
(new reasoning, new exploration, rewriting) cancels the substitution and counts
as rework.

The delegated scope belongs exclusively to the child until it responds. The
root may wait, work on a disjoint scope announced before launch, or ask a
question whose answer cannot change the delegated work. If the root can already
conclude, interrupt the child instead of duplicating the work.

## Complete profiles and reduced fallback

Use the installed `scout`, `researcher`, `runner`, `builder_luna`, `builder`, `visual_operator`, `writer`, `strategist`, and `architect`
profiles. `quota-orchestrator-setup` installs them in the current project with
their fallback settings and complete contracts. Effective permissions remain
subject to the parent runtime, which takes precedence over child sandbox defaults.
## Compare models independently of roles

Roles define missions, restrictions, and deliverables. They do not rank models
or effort levels. Compare all six models for the task; this project establishes
no universal ranking of quality or token consumption.

| Model | Project candidacy | Boundary to preserve |
|---|---|---|
| GPT-6 Luna | Bounded work; `high`, `xhigh`, and `max` are candidates, including well-defined implementation or framing | User floor `high` in named roles and the generic agent. About 20x cheaper than Sol 6.1 per token: see the cost rule. |
| GPT-6 Sol | Ordinary candidate for technical missions and complex interactions, independently of role | Same quality gate and comparison protocol as Sol 6.1, no proof tied to its age; same rates as 6.1 except cached input, 2x more expensive. |
| GPT-5.6 Sol | Ordinary candidate for reasoning, framing, and other missions it can fulfill | Same requirements as other Sol models; no compatibility-only exception or presumed inferiority; rate is 2x that of 6.1 (promotional, see the cost rule). |
| GPT-6.1 Sol | Candidate across implementation, research, and decisions | Being newer establishes neither fewer tokens nor an optimal replacement for other Sol models. |
| GPT-6.1 Terra | Vision through `visual_operator` and clear writing through `writer` | `medium` fallback; `high`/`xhigh` for established difficulty. Half the Sol 6.1 token price; no demonstrated project savings. |
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

### GPT-6.1 Terra: visual tasks

Terra is a candidate when image understanding or precise computer interaction
is needed: screenshot inspection, layout validation, and bounded UI workflows.
The `visual_operator` role does not replace `builder` for design and integration
or Luna for textual or mechanical work. Prefer sufficient connectors and APIs;
small actions stay with the primary. Delegation must amortize coordination or
serve an explicit visual capability need, with an action budget and observable
stop condition.

| Task | Candidate Terra effort | Condition |
|---|---|---|
| Explicit workflow, readable screenshots, direct validation | `medium` (fallback profile) | Observable criteria and available tools |
| Ambiguous states, multiple visual constraints | `high` | Ambiguity identified before dispatch |
| Difficult spatial or perceptual reasoning | `xhigh` | Established difficulty and planned validation |

`low` may be evaluated for simple contracts when delegation is justified;
`max` is not automatic. The API documents `none`, `low`, `medium`, `high`,
`xhigh`, `max`; this session's runtime also offers `ultra`, absent from the
API model page. Do not equate these lists. A locked profile stays at `medium`;
do not claim an unapplied effort override. Select an available profile that
preserves the contract, or keep the work with the primary.

Sources consulted October 26, 2026:
[Terra](https://developers.openai.com/api/docs/models/gpt-6.1-terra),
[Luna](https://developers.openai.com/api/docs/models/gpt-6-luna),
[Sol 6.1](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
[changelog](https://developers.openai.com/api/docs/changelog).
Terra's page highlights vision, computer interaction, and clear writing. This
does not establish general superiority or this project's cost per accepted
result. Terra standard prices per million tokens: input $1, cached input $0.05,
30-minute cache writes $1.25, output including reasoning $5. At equal token
counts and service level, Terra costs half as much as Sol 6.1, and 10 times Luna
for input, writes, and output, 5 times Luna for cached reads. Compare full cost
after validation; token prices alone do not prove savings. Other prices above
retain their stated observation date; no project benchmark is added here.

### GPT-6.1 Terra: clear writing

The `writer` role uses Terra for substantial drafting, rewriting, and synthesis
from established facts: documentation, explanations, and user-facing text.
Provide the audience, objective, sources, constraints, and acceptance criteria
before dispatch. New factual research stays with `researcher`; technical decisions
stay with the primary or the appropriate role. Small edits stay at the root,
and Luna remains a candidate when its capacity suffices. The model page's clear
writing capability supports this candidacy, not demonstrated superiority.

| Writing task | Candidate Terra effort | Validation |
|---|---|---|
| Scoped drafting or rewriting for a known audience | `medium` (fallback profile) | Factual fidelity, clarity, tone, and format |
| Synthesis of established material with delicate nuances or interdependent constraints | `high` if applied by the runtime | Preserve meaning, caveats, numbers, and provenance |

Length alone does not justify `high`, `xhigh`, or `max`. Missing or contradictory
facts are reported to the primary, never invented. The same effort-override and
full-cost rules as for `visual_operator` apply. The role does not publish or send
text to third parties without explicit authorization. This candidacy is based
on the [Terra model page](https://developers.openai.com/api/docs/models/gpt-6.1-terra),
consulted October 26, 2026; quality and cost benefits remain unmeasured.

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

If the user explicitly postpones setup, the reduced fallbacks below may be used
for an immediate task. Include the relevant contract directly in the child
prompt and state that guarantees are reduced.

### Scout — `scout`, reduced fallback `explorer`

Read only, including scout_complex. Explicitly assign causal investigation
or bounded review. A causal investigation stops at a sufficient evidence chain
(entry point, relevant flow, localized cause, paths and lines). A bounded review
covers all assigned axes; the first bug does not complete it. Complex review
does not require known contradictions. Modify nothing. Stop after three
unsuccessful searches and report eliminated hypotheses and unverified areas;
the limit never implies conformity.

### Researcher — `researcher`, reduced fallback `default` with task-selected model/effort

External research only. Cite URLs, dates, and versions; separate facts from
interpretations; flag contradictions. Five queries maximum. Modify no files
and delegate to nobody.

### Runner — `runner`, reduced fallback `default` with task-selected model/effort

Run an already defined validation and report the command, exit code, tested
scope actually tested, and essential error. Separately include test-runner
completion evidence (final summary, expected count, or suitable terminal marker),
failures, exclusions, and checks not performed. Code 0 alone means validation
not established, not economic non observable; no universal marker is required.
Fix only an obvious local mistake. At most three
fix-test cycles, or two for an environment problem. Do not redesign.

### Builder — `builder_luna` or `builder`, reduced fallback `worker`

Use `builder_luna` for a fully specified scope with clear constraints and reliable
targeted validation; use `builder` when design, tradeoffs, or integration remain.
Implement the smallest defensible change. Do not expand
architecture, APIs, schemas, or dependencies without authorization. Validate
the change narrowly, with command, measured exit code, tested scope, and
test-runner completion evidence (summary, expected count or terminal marker).
Report failures, exclusions and unperformed checks; code 0 alone means validation
not established. No universal marker or economic non observable status.
Stop after three attempts and report the decision or failure.

### Visual operator — `visual_operator`, no automatic fallback

Use GPT-6.1 Terra `medium` for substantial screenshot inspection, visual layout
validation, and bounded computer workflows. Supply surfaces, acceptance criteria,
an action budget, and an observable stop. Prefer sufficient connectors and APIs.
For computer interaction, follow the applicable computer-use skill. The role
inherits the parent's tools and permissions; its name does not grant UI access.
It does not design architecture or implement general code. Select `high` for
identified state ambiguity and `xhigh` for established perceptual difficulty only
when runtime settings are actually applied; otherwise keep the work at the root
or use an available profile preserving this contract. Report observed evidence,
actions, unverified criteria, and limits; never infer success from an unseen UI.

### Writer — `writer`, no automatic fallback

Use GPT-6.1 Terra `medium` to draft or rewrite substantial text from established
facts. Supply the audience, format, source material, and acceptance criteria.
Select `high` for delicate synthesis only when the runtime applies that setting;
otherwise keep the work at the root or use an available profile preserving the
contract. Check meaning, numbers, caveats, provenance, and editorial criteria.
Missing facts go to the primary; the writer does not perform research, modify
executable code, or publish/send without explicit authorization.

### Strategist — `strategist`, no fallback

Read only and context bound. Turn already assembled evidence into a decision,
decomposition, execution order, role assignments, contracts, and acceptance
criteria. Do not explore, execute commands, write files, or spawn agents. The
primary agent performs the actual orchestration. Do not insert this role before
an implementation whose contract is already explicit, and do not escalate to
Astra when a targeted measurement can settle the question.

### Architect — `architect`, no fallback

Rare use: a conceptual decision based on an already assembled context packet.
Keep the existing consultation budget: zero without need, one initial call,
at most two per standard task. Announce the remaining budget. A second call
requires new facts or a remaining technical contradiction that could invalidate
the decision; no systematic second opinion or retry on the same failure.
Beyond that, request a new budget. Aim for a context packet of about 60 lines
and a deliverable of about 80 when sufficient; never omit decisive evidence
or conditions to meet those targets.
If it is unavailable or the restrictions cannot be guaranteed in the session,
do not consult the Astra architect subagent. The deliverable contains a
diagnosis, recommendation, alternatives and risks, and required measurements,
without a patch.

<!-- contract:execution -->
Architect restrictions apply to the consultant subagent; they do not limit an
Astra root selected by the user. The consultant performs no exploration,
commands, writes, or delegation and uses only the supplied context. Distinguish
announced model, configuration, and attested execution: use effective metadata
when accessible (role, model, effort), otherwise state "execution not verified".
Inherited instruction provenance is not proof of the executing model. After the
response, verify in the trace the architect role, model, announced effort, and
absence of tool calls; without effective architect + gpt-6-astra + announced
effort evidence, discard the result as noncompliant and do not claim an attested
Astra consultation or consumption.

## Handoff

Use `fork_turns = "none"` unless complete history is explicitly necessary. State
that the child must not reload this skill or delegate.

<!-- contract:mission -->
For a substantial mission, the self-contained handoff names the mission type,
exclusive scope, identified criteria (the user's acceptance criteria),
constraints, analyzed state (commit and relevant local changes, when the root
already knows them: run no command to obtain them), available facts, hypotheses,
unknowns and validations, stopping condition, and decisions to escalate to the
root. A simple mission may use a few sentences; no file or JSON format is
mandatory.

Do not turn a hypothesis into a fact in the synthesis. Preserve caveats,
conditional alternatives, and measurements still needed.

## Measurement and validation

Apply the paired measurement protocol above. A run with `Complete = false`
is exactly `non observable`; never use its tokens or duration in economic
comparisons. Complete failures remain observable and must be included.

Targeted validation belongs to the agent making the change.

<!-- contract:review -->
Independent review remains conditional and never systematic: one focused review
is justified for security, data loss, an irreversible migration, a public
contract, an unresolved contradiction, or missing reliable tests for critical
behavior. When such a risk is actually affected, the root explicitly decides
whether its checks suffice or one focused review is necessary. No systematic
additional reviewer; architect is not the final tester.

Never widen permissions or use `--yolo` or
`--dangerously-bypass-approvals-and-sandbox` to enable delegation.

## Mission contract and final acceptance

<!-- contract:coverage -->
The return maps every identified criterion to “verified”, “failed”, or
“not verified”, with evidence and the state it applies to. Findings retain
stable identifiers and distinguish confirmed defect, risk, and improvement
proposal. Preserve caveats and unknowns explicitly.

<!-- contract:closure -->
Delegation transfers execution, not responsibility for closure.
After the return, the root reconciles initial criteria with results, flags
missing coverage, examines the relevant diff after implementation, and checks
that evidence matches the final state. It performs targeted acceptance checks
without repeating the child's exploration: reading a diff costs input tokens,
only a redo cancels the substitution. Declare work complete only when all
required criteria are satisfied; otherwise state the limits or blocker.

<!-- contract:freshness -->
Any later modification invalidates evidence it may affect. Rerun only the
affected checks and report changes since validation; reuse other evidence
when its relevant state is unchanged.

<!-- contract:completion -->
Builder and runner separately report the command, measured exit code, scope
actually tested, and completion evidence specific to the test runner: final
summary, expected count, or suitable terminal marker. Report failures,
exclusions, and checks not performed. Code `0` without sufficient evidence
means “validation not established” (French: « validation non établie »); the
root judges whether the evidence suffices. Do not use the economic status
`non observable` for this; no universal marker such as `PASS` is required.

<!-- contract:scout-modes -->
Scout and scout_complex have two explicitly assigned modes; unassigned means
causal investigation:
- Causal investigation: stop when a sufficient evidence chain answers the
  question (entry point, relevant path, localized cause, evidence).
- Bounded review: stop after all assigned axes are covered, identifying
  unverified areas. Finding the first bug does not complete the mission.
Existing search bounds still apply; reaching them produces an explicit limit,
never an implicit conclusion of conformity. A complex review does not require
previously known contradictions, but an established Sol-level capacity need.

Reduced fallbacks receive the mission, coverage, and completion clauses above in
their prompt, with guarantees stated as reduced.
