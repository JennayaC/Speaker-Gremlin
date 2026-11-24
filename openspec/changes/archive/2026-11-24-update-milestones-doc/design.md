# Design

## Context

See proposal.md for why. Facts from the code that the new text must match:

- Drift is the 3rd plain argument to `src/speaker_node.py` (`run_cluster.py` uses `NodeA 5003 0`, `NodeB 5004 50`, `NodeC 5005 -100`).
- `get_drifted_time()` returns start wall time + (elapsed monotonic time × (1 + drift_rate)).
- The coordinator measures drift by comparing each heartbeat's `sender_ts` to its own receive time and prints `[NodeX] Expected: ... | Local: ... | Error: ...ms` (`src/coordinator.py:56-58`).
- Rejoin: after 2.5s with no heartbeat the coordinator marks a node lost; when a heartbeat shows up again it prints `Node X is back online!` and sends that node a `STATE_SNAPSHOT` (`src/coordinator.py:73-78`, `113-119`). Nodes never send a rejoin message.

## Goals / Non-Goals

**Goals:**
- Every statement in M5 and M6 matches the code.
- M7 is written clearly enough that the next change (building it) can be proposed straight from it.

**Non-Goals:**
- Changing the M6 learning bullets or experiment text beyond the "rejoin message" bullet.
- Deciding M7's message names, fields, or how often it syncs. That belongs to the M7 build change.

## Decisions

**`[DONE]` goes at the end of the title**, e.g. `## Milestone 0 — Skeleton and first message [DONE]`. This is the choice made on 2026-11-10. M7 has no tag, so you can tell at a glance what's left.

**M6 keeps its idea and changes only the mechanism.** "How does a returning node catch up?" is still the right concept. Only the "You will build" bullets change: the coordinator *detects* the return (heartbeat after being lost) instead of the node *announcing* it.

**M7 uses the coordinator as the time source, with a simple request/reply sync (Cristian's algorithm, the simple idea behind NTP).**
- A node asks the coordinator for the time and notes when it asked (t0) and when the answer came back (t2).
- It guesses the coordinator's time "now" as the reply time + half the round trip, and corrects its clock by the difference.
- Why the coordinator: it already treats its own clock as "expected time" when it prints Error, so syncing to it should make that Error column shrink, which you can actually see.
- Alternatives considered: full NTP (too much: several servers, filtering, gradual slewing); Berkeley-style averaging of all nodes (more messages, and there's no single "right" clock to check against).

**M7's experiment uses the chaos proxy.** Run sync with no delay first, then with delay. The "half the round trip" guess assumes the trip is equally long both ways, and random delay breaks that. This ties M7 to M3/M4 and shows why NTP is never perfectly accurate.

## Risks / Trade-offs

- [M7 text promises behavior the build change later changes] → M7 stays at the "what you'll build" level with no exact message formats; the build change can update it.
- [Proxy currently only relays heartbeats and PLAY] → The M7 experiment says "through the chaos proxy" as a goal; the build change decides whether time messages go through the proxy.
