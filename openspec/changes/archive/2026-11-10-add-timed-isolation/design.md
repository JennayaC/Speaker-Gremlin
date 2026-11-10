# Design

## Context

See proposal.md - Why. The proxy (`src/chaos_proxy.py`) only handles one direction: speaker node heartbeats going to the coordinator. PLAY and STATE_SNAPSHOT go straight from the coordinator to the nodes. The coordinator marks a node as lost (and bumps `state_version`) only for nodes it has already heard from, after 2.5 seconds of silence (`coordinator.py:108-117`).

## Goals / Non-Goals

**Goals:**
- One command line runs steps 1-3 of Experiment C the same way every time.

**Non-Goals:**
- Cutting off coordinator-to-node traffic. It doesn't go through the proxy, and for Experiment C, stopping heartbeats is enough to make the coordinator think NodeA is gone.
- More than one window per run.

## Decisions

**1. Start time is "seconds after the proxy starts", not "after the first heartbeat from the node".**
- Why: simpler, and heartbeats arrive within a second or two anyway, so a start of a few seconds is enough for the coordinator to see NodeA first.
- Alternative: wait for the target's first heartbeat, then start counting. More exact, but needs extra state to remember the first time the node was seen. Can be added later if the timing turns out flaky.

**2. Two separate switches (start + length), not one combined switch.**
- Why: matches the existing style (`--drop`, `--max-delay` each take one number) and keeps `--target-node` as the only place that names a node.
- Alternative: reuse `--drop` (e.g. `--drop NodeA 10`). Rejected because `--drop` already means a drop probability.

**3. The time check runs inside the existing packet drop step, before the random drop and delay.**
- Why: packets in the window are dropped no matter what, so it makes sense to check that first. It reuses the existing `is_target` check.

**4. Use `time.monotonic()` for the proxy start time and the "now" reading.**
- Why: this is a stopwatch question ("how long since start?"), and a monotonic clock never jumps if the wall clock changes.

## Risks / Trade-offs

- [Window too short: under 2.5s the coordinator never declares NodeA lost, so no version bump happens] -> Use an `--isolate-for` well over the 2.5s timeout (e.g. 10s).
- [Start too early: NodeA cut off before the coordinator hears from it] -> Start the nodes and coordinator before the proxy's window opens; a start of about 5s is enough.
- [Clocks are per process: the window counts from when the *proxy* starts, not the cluster] -> Start the proxy together with the others (e.g. via `run_cluster.py`) so the timings line up.
