# Proposal

## Why

Right now, to run an experiment you open `src/run_cluster.py` and comment lines in or out (the proxy line, the coordinator line). It is easy to forget a line and run the wrong setup, and the file fills up with old commented-out commands. A named switch makes each experiment one command you can repeat.

## What Changes

- `src/run_cluster.py` gets an optional `--experiment <name>` switch.
- Each experiment name maps to the chaos proxy command it needs, and to whether the coordinator starts with the cluster.
- Names added now:
  - `A`: chaos proxy drops 70% of NodeA's heartbeats and delays the rest by up to 3.5s. Coordinator starts with the cluster. (Delay alone was tried first: some heartbeat almost always arrived within the 2.5s timeout, so NodeA was never declared lost.)
  - `C`: chaos proxy cuts off NodeA from 5s to 15s. Coordinator does **not** start with the cluster (you run it in its own terminal so you can restart it).
- With no `--experiment`, the cluster starts everything normally: coordinator, a chaos proxy that breaks nothing, and the 3 nodes. This matches what the README "Quick way" already says. Before this change the coordinator line was commented out.
- An unknown name stops with an error that lists the valid names, and starts nothing.
- The old commented-out command lines are removed from `run_cluster.py`.
- Docs updated: Experiment C "How to run it" in `docs/milestones.md` uses `--experiment C` instead of commenting lines; Experiment A gets a short "How to run it"; README mentions the switch.

Out of scope: Experiment B. It needs a duplicate mode in the chaos proxy, and PLAY does not go through the proxy today. That is a separate, later change.

## Capabilities

### New Capabilities
- `cluster-launcher`: how `run_cluster.py` starts the cluster processes, including picking a named experiment setup.

### Modified Capabilities
<!-- none -->

## Impact

- Code: `src/run_cluster.py` only. No changes to the coordinator, speaker nodes, or chaos proxy.
- Docs: `docs/milestones.md` (Experiments A and C), `README.md` (Quick way section).
