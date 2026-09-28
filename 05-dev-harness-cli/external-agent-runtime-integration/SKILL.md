---
name: external-agent-runtime-integration
description: "Use when integrating an external agent CLI runtime."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agent-runtime, cli, subprocess, streaming, integration-testing]
---

# External Agent Runtime Integration

Integrate an agent CLI as a delegated runtime, not as an OpenAI-compatible model provider. Keep protocol-specific behavior behind a transport, session, and event projector; surfaces consume the host application's existing contracts.

## Procedure

### 1. Map the installed runtime empirically

Use a temporary workspace and the safest supported mode. Record exact version, argv, input records, output events, exit codes, stderr, session identifiers, model catalog, timeout behavior, and denied actions.

Run the equivalent of:

```bash
<runtime> --version
<runtime> --help
<runtime> models
<runtime> --input-format stream-json --output-format stream-json --sandbox --print='probe'
```

Prefer official NDJSON/RPC output. Never make regexes over human terminal prose the primary protocol. Treat undocumented fields as optional and preserve unknown structured records for diagnostics.

### 2. Write vertical contract tests before production code

Cover one end-to-end behavior per cycle:

1. fake executable accepts the observed input record;
2. transport parses structured events and terminal result;
3. projector correlates tool start/completion;
4. session resumes with the observed conversation identifier;
5. host agent lifecycle cancels and closes the subprocess;
6. inventory exposes the runtime and its models;
7. selecting a model reaches the child process argv.

Make the last two separate assertions. A populated picker does not prove the selected value reaches execution.

### 3. Build three narrow layers

- **Transport:** discovery, version/auth/model probe, argv, stdin/stdout, bounded stderr, deadlines, cancellation, process-tree cleanup, environment isolation, optional redacted protocol log.
- **Session:** one conversation identifier, busy/closed state, interrupt event, projector ownership, retirement after fatal errors.
- **Projector:** structured runtime events into existing host messages/tool events; no frontend-specific protocol.

Reuse one stateful projector for the whole turn. Recreating it per event loses tool correlation and session metadata.

### 4. Treat model discovery, switching, and execution as one feature

Parse model IDs from the runtime's live catalog and expose `auto` plus discovered IDs in the existing picker payload. When the catalog command is network-backed, measure a cold authenticated run and give the first picker request a bounded deadline that exceeds the observed latency. Test that the **first returned catalog** already contains discovered models; a second-call cache test does not prove the user can select them.

Use background discovery only when completion has an observable path back to the open picker (event, query invalidation, or bounded refetch). Do not return `auto` first and silently fill a backend cache later: frontend query caches can keep that incomplete response indefinitely.

When a concrete model is selected, pass the exact identifier through picker → shared provider resolver → live agent swap → session → transport → child argv. When `auto` is selected, omit the model override so the runtime owns routing.

Register the delegated provider in every identity layer used by model switching, not only in the inventory builder. A picker row proves discovery but does not make the shared switch resolver recognize the provider.

If provider registration also produces a metadata-only inventory row, replace or merge that row with the live runtime row. Never leave two rows with the same slug: consumers commonly select the first and can see an empty catalog while the populated row exists later.

Handle live swaps as delegated-runtime lifecycle changes:

- allow the delegated API mode to have an intentionally empty HTTP `base_url` and clear any endpoint inherited from the previous provider;
- never construct an OpenAI/Anthropic client for a delegated destination;
- retire an existing delegated session when its model changes so the next subprocess receives the new argv;
- retire the delegated session when switching away from it.

Never hardcode a picker to `auto` after proving that the runtime publishes models. Add tests for all three boundaries:

```text
inventory.models == [auto, ...discovered]
model_switch(provider=<runtime>, model=<id>).success == true
child_argv contains --model <selected-id>
```

Finally run a real vertical smoke test through the same resolver and live-swap methods used by the Desktop, then execute a turn and assert both the selected model and final response. A direct transport call alone does not prove that clicking the picker works.

### 5. Fail closed at protocol boundaries

Do not invent approval replies. If headless mode cannot request interactive approval, surface denied actions as a partial/error result instead of reporting success with empty output. Unknown event discriminators that explicitly represent approval or permission requests must interrupt and retire the session; ordinary untrusted text containing words such as “permission” must not trigger the fail-safe.

A terminal “success” is not sufficient when the payload includes denied actions or zero executed turns.

Treat host approvals and child-runtime permissions as separate gates. A host-level YOLO setting does not automatically authorize a delegated subprocess. When the user explicitly requests unrestricted execution:

1. confirm the child CLI's exact unsafe flag from its live `--help`;
2. expose it as an explicit, default-off profile setting rather than an environment variable;
3. make unsafe and sandbox flags mutually exclusive in argv — unsafe wins only when explicitly enabled;
4. propagate the setting through the runtime config reader and default client factory, not only the transport constructor;
5. write settings through the host's supported config command, read back every effective value, then restart any long-lived backend;
6. smoke-test a harmless real tool action and verify the structured tool state reached completion, the unsafe flag is present, and the sandbox flag is absent.

Never infer child YOLO from the host approval mode: collapsing the two gates creates a hidden privilege escalation for users who only intended to suppress host prompts.

### 6. Harden subprocess ownership and liveness

Coordinate every liveness clock that can terminate the turn. A transport timeout and a host-level turn watchdog are independent cancellation authorities: renewing only the transport deadline still lets the host abort a healthy long-running turn.

For each substantive structured event:

1. renew the transport's protocol-inactivity deadline;
2. call the host's canonical activity callback so its timestamp and description advance;
3. make that callback best-effort so telemetry failure cannot drop the underlying event.

Count assistant deltas, meaningful progress, and tool lifecycle transitions as activity. Do not let unknown events or empty keepalives renew liveness indefinitely, because noise would mask a real stall. If the child runtime also imposes an absolute print/request ceiling, disable it or place it above the host policy; two competing deadlines produce misleading failures.

Write regressions that prove both sides: a turn emitting substantive events longer than the watchdog window survives, while a silent child is still cancelled. Assert that a raising activity callback does not suppress event delivery.

- Start a separate process group where supported.
- On interrupt: signal, wait briefly, kill the process tree, then reap.
- Bound queued events, retained events, stderr, startup time, request time, and shutdown time.
- Do not inherit unrelated host credentials when the delegated runtime owns authentication.
- If protocol logging is enabled, create the file with restrictive permissions and redact prompts, content, outputs, tokens, cookies, and authorization fields recursively.

### 7. Persist truthful resume state

Store the runtime conversation identifier in metadata attached to a persisted projected message. Restore it from the transcript when constructing a cold agent. Capture identifiers from initialization events as well as terminal results because some runtimes omit them at completion.

Convert cumulative usage reported by the runtime into per-turn deltas before adding it to host session counters.

### 8. Verify the real resolution chain

Use the repository's canonical test runner. Then verify:

- focused runtime contracts;
- regressions for the reference delegated runtime;
- gateway/generated contracts;
- desktop typecheck;
- syntax/compile checks and clean diff;
- real binary probe;
- real tool turn;
- real two-turn resume;
- real explicit-model turn;
- real denied-action behavior.

After changing backend code, remember that an already-running desktop/backend process may still hold the old modules. Report that a restart is required instead of claiming the live picker changed before the process reloads.

## Completion report

Report only:

- layers implemented;
- exact test counts and real probe results;
- known protocol limitation versus implementation gap;
- branch/commit and whether it was pushed;
- whether a backend restart is required.

Do not call the feature complete while the picker advertises a choice that execution ignores, or while execution supports models the picker hides.
