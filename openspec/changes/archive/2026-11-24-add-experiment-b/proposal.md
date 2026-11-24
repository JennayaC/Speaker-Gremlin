# Proposal

## Why

Experiment B ("what happens when the same PLAY command arrives twice?") is the only experiment you can't run with a switch. Its findings came from editing the coordinator by hand to send each PLAY twice (the commented-out line in `src/coordinator.py`). The docs tell you to "use the chaos proxy's duplicate mode", but that mode doesn't exist, and PLAY never passes through the proxy, so the proxy couldn't copy it anyway.

## What Changes

- The coordinator sends PLAY to the chaos proxy instead of straight to each node. Each PLAY says which node port it is for.
- The chaos proxy relays PLAY to that node.
- The chaos proxy gets a new `--duplicate` switch: a 0.0 to 1.0 chance that a PLAY is sent to the node twice (like `--drop`).
- Drop, delay, and isolation keep applying to heartbeats only. PLAY is never dropped or delayed, so Experiments A and C behave exactly as before.
- STATE_SNAPSHOT still goes straight from the coordinator to the node. Only PLAY goes through the proxy.
- The commented-out "send PLAY twice" line in `src/coordinator.py` is removed. The proxy does that job now.
- `src/run_cluster.py` gets `--experiment B`: coordinator on, proxy with `--duplicate 1.0`, the three nodes.
- `docs/milestones.md` Experiment B gets "How to run it" steps. `README.md` mentions `--experiment B`.

Out of scope:
- Sending STATE_SNAPSHOT to every node when the coordinator shifts `target_play_time` (a separate, later change).
- Coordinator catching up to node versions after a restart (a separate, later change).

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `chaos-proxy`: relays PLAY commands from the coordinator to nodes, and can send each PLAY twice with `--duplicate`.
- `cluster-launcher`: adds the Experiment B setup; `B` becomes a valid `--experiment` name.

## Impact

- Code: `src/chaos_proxy.py` (PLAY relay and `--duplicate`), `src/coordinator.py` (PLAY goes to the proxy, old duplicate line removed), `src/run_cluster.py` (`B` entry). `src/speaker_node.py` doesn't change, since it already drops duplicate PLAYs by `cmd_seq`.
- Docs: `docs/milestones.md` (Experiment B), `README.md` (Quick way).
- Behavior: every run now sends PLAY through the proxy. If the proxy isn't running, nodes never get PLAY. `run_cluster.py` always starts the proxy, so this only matters when starting processes by hand.
