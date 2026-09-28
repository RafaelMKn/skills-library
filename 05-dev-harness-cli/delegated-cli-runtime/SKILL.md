---
name: delegated-cli-runtime
version: 1.0.0
description: "Use when integrating a structured external agent CLI."
metadata:
  hermes:
    tags: [runtime, cli, subprocess, ndjson, streaming, integration, agent]
---

# Delegated CLI Runtime

Integrate an external coding-agent CLI as a first-class runtime in a host agent or desktop app. Use this for machine-readable subprocess protocols such as NDJSON, JSON-RPC, or event streams. Do not use this workflow for ordinary OpenAI-compatible model providers.

## Required procedure

### 1. Establish the architectural boundary

1. Read every repository instruction file that governs the transport, agent loop, gateway, persistence, tests, and desktop areas.
2. Trace one existing delegated runtime end to end before editing: resolver → agent initialization → turn dispatch → transport/session → event projection → persistence → inventory/UI.
3. Keep the external protocol behind three boundaries:
   - **transport/client**: binary discovery, argv, stdin/stdout, process lifecycle;
   - **session**: conversation identity, cancellation, one active turn, retirement;
   - **projector**: external events into the host's existing message/tool/status contracts.
4. Make the Desktop and Gateway consume existing host contracts. Never make the frontend spawn the CLI or understand its private protocol.

### 2. Probe the installed CLI before designing the adapter

Use a temporary workspace, sandbox/restricted mode, and no permission-bypass flag. Record the exact binary version and command syntax.

Probe, in order:

1. `--help`, `--version`, model/capability listing, and authentication status.
2. A minimal successful turn with structured input and structured output.
3. Every event discriminator and nested step/tool discriminator actually observed.
4. Malformed input and non-zero exit behavior.
5. Session continuation using the runtime's conversation handle.
6. A harmless read-only tool call.
7. A tool that requires permission, to learn whether headless mode supports approval, auto-denies, or blocks.
8. Timeout and cancellation behavior.

Persist a redacted report and a deterministic probe script. Treat observations as version-scoped facts, not universal protocol guarantees.

**Pitfall:** Never infer the wire format from human terminal text; localized or redesigned output silently breaks regex adapters.

**Pitfall:** Check whether flags require `--flag=value` rather than `--flag value`; some print/headless CLIs parse these forms differently.

### 3. Specify the protocol from evidence

Document:

- exact input envelope;
- event and step discriminators;
- terminal success/error semantics;
- tool start/completion correlation fields;
- conversation-resume argument and returned handle;
- whether usage is per-turn or conversation-cumulative;
- permission behavior in headless mode;
- minimum verified CLI version.

Unknown events remain unknown. Preserve them for diagnostics, but do not project guessed semantics.

### 4. Build the transport as a bounded subprocess adapter

The client must:

- discover an explicit binary or resolve `auto` with `shutil.which`;
- construct argv as a list, never shell-concatenate user content;
- send the observed structured input exactly, including required role/discriminator fields;
- use separate startup, request, and shutdown timeouts;
- stream events through a bounded queue and retain only a bounded diagnostic tail;
- cap stderr retention;
- cancel the whole process tree, wait for exit, then escalate to kill;
- use POSIX process groups and the Windows process-group equivalent;
- serialize access or reject concurrent turns explicitly;
- distinguish protocol failure, process failure, timeout, cancellation, denied action, and incomplete/partial result.

Do not inherit unrelated host credentials by default. Add only the environment the delegated runtime needs for its own authentication.

**Pitfall:** Join stderr/stdout reader threads before snapshotting diagnostic buffers; otherwise error reports race with active writers.

**Pitfall:** A terminal event with partial text is not automatically success. Inspect terminal status, denied actions, completion reason, and process return code together.

### 5. Project events with one stateful projector per turn

The projector owns tool correlation and progressive state for the entire turn. It should emit host-native:

- assistant progress/text;
- tool start/update/completion;
- command/file metadata when officially exposed;
- visible warnings and errors;
- final response and usage/status metadata.

Use observed stable identifiers. If a protocol omits a tool ID but provides a documented step index, derive correlation from that index; do not invent sequence fallback from unrelated fields.

Project an event once. If the session projects it before invoking the UI callback, pass the projection to the callback instead of feeding the same event into a second projector.

**Pitfall:** Detect permission requests from protocol discriminators and status fields, never by searching arbitrary model/tool text for words such as “permission”; untrusted output can trigger false fail-closed behavior.

### 6. Make session and lifecycle semantics explicit

- Allow only one active turn per session unless the protocol proves safe concurrency.
- Treat interrupt while idle as a no-op so it cannot poison the next turn.
- During an active turn, set the cancellation event and call the client's process-tree cancellation.
- Preserve already projected rows on timeout, cancellation, or protocol failure and mark the result partial.
- Retire the session after failures that make continuation unsafe.
- Close and clear session/client state from the host lifecycle, including usage baselines.

### 7. Persist and resume without protocol leakage

Store the external conversation handle in metadata attached to a persisted host message. On cold reconstruction, scan persisted transcript metadata and restore the newest valid handle before creating the next turn.

Capture the handle from every protocol location where the verified CLI may emit it, including initialization and terminal events.

Do not report persistence as successful merely because in-memory messages were appended. Propagate the actual database flush result.

If usage counters are conversation-cumulative, store a per-session baseline and expose non-negative deltas per turn. Reset the baseline when the delegated session retires.

### 8. Expose the runtime through the existing inventory

The resolver should map a provider/runtime slug to a dedicated API mode and pass explicit binary, model, sandbox, timeout, and debug settings. In delegated mode, skip construction of normal OpenAI/Anthropic clients when the CLI owns authentication and tool execution.

Populate the existing provider/model inventory with probed availability, authentication, version, models, and runtime status. Do not assume “binary installed” means “authenticated.”

### 9. Make diagnostics opt-in and privacy-preserving

Protocol logging is off by default. When enabled:

- resolve logs under the profile-aware application home;
- create files with owner-only permissions where supported;
- redact recursively by sensitive key;
- also redact message content, tool inputs/outputs, command output, and conversation IDs;
- never include inherited environment values.

Key-name redaction alone is insufficient because prompts and tool output routinely contain secrets under generic keys such as `content` or `text`.

### 10. Test in layers, then run the real CLI

Use a fake executable for deterministic tests of:

- argv and exact input envelope;
- fragmented/malformed NDJSON;
- bounded stderr/events and backpressure;
- timeout and process-tree cancellation;
- active versus idle interrupt;
- terminal errors, denied actions, and partial output;
- debug-log permissions and redaction;
- tool start/completion correlation;
- cold resume from persisted metadata;
- cumulative-usage delta;
- inventory/authentication states;
- regression of the reference delegated runtime.

Then run safe real probes in a temporary workspace:

1. read a known marker file through the delegated runtime;
2. execute two turns and prove the second resumes the same conversation;
3. request one harmless permission-gated action and verify denial is loud rather than reported as success;
4. run the Desktop typecheck/build and generated Gateway contract tests;
5. run the repository's canonical test runner, syntax checks, and `git diff --check`.

A unit suite does not replace a real protocol smoke test, and a successful subprocess exit does not replace asserting the projected final result.

## Approval decision rule

If official headless documentation and empirical probing show no interactive approval channel, document that boundary and fail safely on denied actions. Do not invent an approval round-trip, enable a global dangerous bypass, or claim feature parity that the upstream protocol cannot provide.

## Delivery report

Report only verified facts:

- branch/commit or exact modified paths;
- focused and regression test counts where captured;
- real smoke-test outputs;
- protocol/version scope;
- upstream limitations, especially permission approval;
- checks not run and why.

Separate “implemented” from “upstream cannot expose this in headless mode.”
