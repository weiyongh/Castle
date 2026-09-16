# Castle Agent Reference Folder

## Purpose

This document defines the **reference working-directory structure for a
Castle Person**.

`People` is a logical Castle concept. A Person is a capability entity
with a clear responsibility. When a Person is currently implemented as a
Codex Agent/Project, its directory is also its real working directory.

The purpose of this reference structure is not to prescribe a complete
Agent framework. It provides only a small, practical home for the kinds
of persistent material already known to matter for work and future
self-reboot.

## Reference Structure

``` text
<person>/
├─ AGENTS.md
├─ README.md
├─ src/
├─ doc/
├─ work/
├─ tasks/
└─ context/
   ├─ trace/
   └─ chat/
```

For example:

``` text
castle/
└─ people/
   └─ acqplanner/
      ├─ AGENTS.md
      ├─ README.md
      ├─ src/
      ├─ doc/
      ├─ work/
      ├─ tasks/
      └─ context/
         ├─ trace/
         └─ chat/
```

## Directory Roles

### `AGENTS.md`

The Person's stable **Project Context**.

It should contain durable information needed for a fresh compatible AI
to understand what Person it is becoming: identity, responsibility,
boundaries, working principles, Castle relationships, and necessary
Context/Asset access.

It should not become a container for transient task state.

### `README.md`

The human-readable entrance to the Person's workspace.

It explains what the workspace is, how it is organized, and any
practical information needed to enter or use it. Keep it short unless
real work creates a need for more.

### `src/`

Reusable implementation capability that the Person has already
materialized.

Examples may include programs, parsers, generators, utilities,
algorithms, or other code created through real work.

An empty `src/` is valid. Do not create code merely to make the
workspace look complete.

### `doc/`

Durable documentation and knowledge developed by the Person.

This is where stable working knowledge, methods, design explanations,
tool documentation, and other reusable understanding can settle after it
has matured beyond temporary work.

`doc/` is not the Person's identity; that belongs in `AGENTS.md`.

### `work/`

The Person's working desk.

Drafts, temporary analyses, exploratory files, intermediate artifacts,
scratch work, and material whose long-term identity is not yet known may
live here.

The purpose of `work/` is to let the Person work freely without
requiring every intermediate artifact to be classified as a permanent
asset before it has proved useful.

### `tasks/`

Formal work units with an identifiable objective.

A task may contain its inputs, task-specific context, outputs, and other
material required to complete that piece of work.

The reference structure does **not** prescribe `current/`, `history/`,
task IDs, status machines, gates, or lifecycle rules. Those should
appear only if repeated real work proves they are useful.

### `context/trace/`

Necessary decision or reasoning trace that cannot be reconstructed
adequately from resulting code, documents, tasks, or Assets.

Trace should be selective. It exists to prevent a rebooted Person from
losing important working rationale or repeating costly dead ends.

It is **not** intended to become a complete activity log.

### `context/chat/`

Chat context that remains materially useful to the Person's working
capability and has not yet been fully materialized elsewhere.

Chat is a recovery layer, not the final knowledge store. As a Person
matures, valuable content should progressively settle into `AGENTS.md`,
`src/`, `doc/`, tasks, or Castle Assets where appropriate.

The goal is not to preserve every conversation forever.

## Self-Reboot

A Castle Person should, as it matures, become capable of
**self-reboot**.

For a Codex-based Person, the practical test is:

> In a fresh work environment with no useful prior chat history, can a
> compatible AI enter this working directory, recover the Person's
> identity and necessary working capability from persistent material,
> obtain required Castle Assets/Context, understand the current task,
> and continue useful work?

The current candidate minimum reboot set is:

``` text
Project Context
+ src
+ Task / Trace Context
+ necessary Chat Context
+ required Castle Assets
```

This is a hypothesis to be tested through real reboot attempts, not a
fixed schema.

If a fresh Agent cannot recover, add only the missing persistent
information revealed by the failure.

## Working Flow

Material can naturally move as the Person works:

``` text
work/
  │
  ├─→ src/       reusable implementation
  ├─→ doc/       durable knowledge/documentation
  ├─→ tasks/     formal task artifacts
  └─→ Castle Assets, when the result belongs to the Castle itself
```

`context/trace/` and `context/chat/` provide recovery context where the
other persistent outputs are not yet sufficient.

## Design Rule

**This is a reference folder, not an Agent bureaucracy.**

Do not pre-create registries, schemas, state machines, state
hierarchies, approval gates, archives, logs, or additional directory
layers merely for architectural completeness.

Let each Person earn additional structure through real work.
