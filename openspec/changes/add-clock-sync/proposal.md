# Proposal

## Why

Milestone 7 in `docs/milestones.md` describes clock synchronization, but nothing is built yet: node clocks drift forever, as in Milestone 5. The user wants M7 to run as its own setup (like Experiments A/B/C), showing the original drift and the fixed clock in the same run, plus the "add delay and watch sync get worse" part from M7's experiment.

## What Changes

- **Speaker node:** new optional `--sync` switch (off by default). With it on, every 5 seconds the node asks the coordinator for the time, measures the round trip, and corrects its clock by (coordinator time + half the round trip − its own time). The raw drifting clock keeps running underneath, so both can be reported.
- **Heartbeats (sync on only):** carry both the synced clock (`sender_ts`) and the raw clock (`raw_ts`). With sync off, heartbeats are unchanged.
- **Coordinator:** answers time requests with its current time. When a heartbeat carries `raw_ts`, it prints the raw error and the synced error side by side on one line. Normal runs print exactly as today.
- **Chaos proxy:** passes time requests to the coordinator without drop, delay, or isolation (same rule as PLAY: heartbeat chaos is for heartbeats only). New `--sync-delay` switch adds a random delay of up to that many seconds to time requests only, so the trip to the coordinator is slower than the trip back.
- **Launcher:** two new setups in the experiments list:
  - `--experiment SYNC`: sync on, bigger drift (NodeA 0, NodeB +5000, NodeC −10000 PPM) so the fix is easy to see.
  - `--experiment SYNC-DELAY`: same as SYNC, plus `--sync-delay 0.5` on the proxy.
  - Normal run and A/B/C keep drift 0 / 50 / −100 and no sync.
- **Docs:** M7 in `docs/milestones.md` gets a "How to run it" section and `[DONE]`; README "Quick way" lists the new names.

## Capabilities

### New Capabilities
- `clock-sync`: how a speaker node keeps its clock in step with the coordinator: the sync switch, time request/reply, the clock correction, and how raw and synced error are shown.

### Modified Capabilities
- `node-clock`: "Clock usage" changes: with sync on, the node uses its synced clock (not the raw drifting one) for timestamps and scheduling, and also reports the raw clock in heartbeats.
- `chaos-proxy`: new `--sync-delay` switch; time requests are not affected by heartbeat drop/delay/isolation.
- `cluster-launcher`: new SYNC and SYNC-DELAY setups; the unknown-name error lists the new names.

## Impact

- Code: `src/speaker_node.py`, `src/coordinator.py`, `src/chaos_proxy.py`, `src/run_cluster.py`.
- Docs: `docs/milestones.md` (M7), `README.md` (Quick way).
- New message types on the wire: `TIME_REQUEST` (node → proxy → coordinator) and `TIME_REPLY` (coordinator → node, direct).
- No change to existing runs: without `--sync`, nodes, coordinator output, and Experiments A/B/C behave as before.
- Out of scope: syncing nodes to each other, gradual clock slewing, the "coordinator catches up after restart" change, and the `[Coordinator]` print prefix.
