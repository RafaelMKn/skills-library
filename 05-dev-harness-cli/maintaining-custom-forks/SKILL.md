---
name: maintaining-custom-forks
description: "Use when maintaining a production fork with custom code."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, github, fork, upstream, rebase, production]
---

# Maintaining Custom Forks

Maintain a long-lived production fork whose custom commits must survive upstream releases. A fork preserves code remotely; it does **not** provide automatic compatibility with future upstream changes.

## Standing rules

- Never promise that an update “cannot break” a custom integration. State the narrower verified claim: the custom commits are preserved in the fork, and each upstream update still requires integration plus regression tests.
- Interpret GitHub’s banner precisely: **ahead** means fork-only commits; **behind** means upstream commits not incorporated. “Behind” alone does not prove the custom feature is broken.
- Do not use **Sync fork** blindly for a production fork with custom commits. The button does not run project gates and can surface conflicts or create an unreviewed merge.
- Distinguish four states in every report: code preserved remotely, upstream synchronized, compatibility tested, and running process reloaded. Evidence for one is not evidence for the others.

## Procedure

### 1. Confirm repository identity and a clean baseline

Verify authentication, remotes, current branch, working tree, and exact SHAs before changing history:

```bash
gh auth status
git remote -v
git status --short --branch
git fetch origin
git fetch upstream main
git rev-parse HEAD origin/main upstream/main
```

Confirm `origin` is the maintained fork and `upstream` is the canonical repository. Never infer this from directory names.

### 2. Measure divergence after fetching

Use Git, not a screenshot or a cached GitHub banner:

```bash
git rev-list --left-right --count origin/main...upstream/main
git log --oneline upstream/main..origin/main
git merge-base origin/main upstream/main
```

Report the left/right direction explicitly. Counts can change quickly and may differ from an older screenshot.

### 3. Estimate conflict risk before syncing

Compare files changed by the fork with files changed upstream since the merge base:

```bash
base=$(git merge-base origin/main upstream/main)
git diff --name-only upstream/main...origin/main > /tmp/fork-files
git diff --name-only "$base"..upstream/main > /tmp/upstream-files
comm -12 <(sort /tmp/fork-files) <(sort /tmp/upstream-files)
```

Any overlap requires review; no overlap reduces risk but does not replace tests. Inspect applicable repository instructions before editing conflicted areas.

### 4. Choose merge or rebase deliberately

- Use **merge** when published history is shared and must remain stable.
- Use **rebase** when the fork intentionally maintains a small patch stack and force-push policy is explicit.
- Never force-push a shared branch merely to make the GitHub banner prettier.

Before rewriting history, publish a recoverable backup branch or tag from the current remote SHA. Perform the integration on a dedicated sync branch, not directly on the only production branch.

```bash
git switch -c sync/upstream-main origin/main
git branch backup/pre-sync origin/main
git push origin backup/pre-sync
# Then choose one:
git merge upstream/main
# or
git rebase upstream/main
```

Resolve conflicts by preserving both the upstream contract and the custom behavior; do not mechanically choose “ours” for integration files.

### 5. Prove the custom integration still works

Run the repository’s canonical test runner plus focused tests for every custom feature and every overlapping file. Include compile/type checks, diff checks, and a real smoke test when the integration controls an external runtime.

A clean merge/rebase is not compatibility proof. Do not publish until the focused custom tests and required project gates pass.

### 6. Publish and read back

Push the validated sync branch first. Update production branches only after review. For rewritten history use `--force-with-lease`, never plain `--force`.

```bash
git push -u origin sync/upstream-main
# after validation/review:
git push origin HEAD:main
# rewritten-history case only:
git push --force-with-lease origin HEAD:main
```

When two or more production refs must remain identical, publish them in one atomic operation with an explicit lease for each old remote SHA. Never fall back to separate pushes if the atomic push fails, because partial publication leaves branches representing different tested states.

```bash
git push --atomic \
  --force-with-lease=refs/heads/main:<old-main-sha> \
  --force-with-lease=refs/heads/custom:<old-custom-sha> \
  origin HEAD:main HEAD:custom
```

Read back the exact targets before claiming success:

```bash
git ls-remote origin refs/heads/main refs/heads/sync/upstream-main
git status --short --branch
```

If the application is long-lived, verify whether it is running the new commit and state clearly when a restart is required.

### 7. Automate recurring synchronization safely

Use a deterministic monitor that emits only the current upstream ref SHA. Feed it to the scheduler's change detector so unchanged upstream state suppresses the agent run; timestamps or explanatory text make every tick look changed.

Create the job paused, configure its requested provider/model, inspect the stored job, then resume it. When an arbitrary model is requested, use the cron CLI's explicit model fields rather than a generic “pin current model” operation:

```bash
hermes cron edit <job-id> \
  --model <model-id> \
  --provider <provider-id> \
  --reasoning-effort <level>
```

The scheduled prompt must be self-contained and fail closed:

1. Validate remotes and record the old SHA of every production ref.
2. Work in an isolated temporary worktree; never rewrite the active checkout.
3. Create a local backup before integration, but publish the remote backup only after all gates pass.
4. Abort without publishing on unresolved conflict, missing gate, timeout pressure, or failed smoke test.
5. Publish all coupled production refs atomically with explicit leases, then read them back.
6. Clean the temporary worktree whether the run succeeds or aborts.

Keep the required test set small enough for the scheduler's execution window. If full proof cannot finish within that window, the safe result is a report with no publication—not a reduced gate set or a partial push.

To inspect a manually fired run, check durable run history instead of relying on `last_run_at`: an in-progress job can legitimately have no completed-run timestamp yet.

```bash
hermes cron runs <job-id>
```

Corroborate `running` with the provider subprocess or scheduler logs before reporting that execution is active.

## Completion report

Report:

- fork and upstream SHAs;
- ahead/behind counts after the final fetch;
- overlapping custom/upstream paths reviewed;
- merge or rebase strategy and backup ref;
- exact gates and smoke tests run;
- remote SHAs read back;
- whether the running service was restarted.

Never collapse “the fork contains the feature” into “future updates are safe.”