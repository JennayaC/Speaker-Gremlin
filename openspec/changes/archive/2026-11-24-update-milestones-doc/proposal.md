# Proposal

## Why

`docs/milestones.md` is the single place that tracks the milestones, but it no longer matches the code: nothing shows which milestones are finished, M5 names a `--drift-ppm` switch that doesn't exist, and M6 describes a "rejoin" message that the code never sends. The next piece of work (fixing clock drift, NTP-style) also has no milestone yet, so there is nothing to point the next change at.

## What Changes

- Add `[DONE]` to the titles of Milestones 0–6.
- **M5:** replace `--drift-ppm` with the real usage (drift is the 3rd plain argument, e.g. `python src/speaker_node.py NodeB 5004 50`), and fix the clock formula line so it matches `get_drifted_time()` (start time + elapsed monotonic time × (1 + drift rate)).
- **M6:** replace the "rejoin message" bullet with what really happens: the coordinator notices a lost node's heartbeat is back and sends it a `STATE_SNAPSHOT`; the node does not announce itself.
- **New M7 (planned, not `[DONE]`):** "Clock synchronization", in the same layout as the other milestones (concept, You will build, You will learn, Experiment, Commit message). Docs only: no code is written in this change.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- None. This change only edits documentation, so no spec-level behavior changes (`skip_specs: true`). The M7 behavior gets its spec rules in the later change that builds it.

## Impact

- `docs/milestones.md` only.
- No code, no specs, no README changes.
- Out of scope: building M7, the "coordinator catches up after restart" change, the "snapshot to every node" idea, and the `[Coordinator]` print prefix.
