# Proposal

## Why

Experiment C (The Returning Stranger) needs a node to be cut off for a while and then come back. Today the only way to cut a node off is `--drop 1.0 --target-node NodeA`, which cuts it off forever. To let the node back in, the proxy has to be stopped and restarted by hand, so the timing is different on every run and the experiment can't be repeated the same way.

## What Changes

- The chaos proxy gets two new command-line switches:
  - one that says **when** the cutoff starts (seconds after the proxy starts)
  - one that says **how long** the cutoff lasts (seconds)
- During that time window, every heartbeat from the target node is dropped. Before and after the window, the target node's traffic acts as it does now.
- The cutoff uses the same target rule as `--drop`: only the node named by `--target-node`, or every node if no target is given.
- When the new switches are not given, the proxy works exactly like it does now.
- Working names for the switches: `--isolate-after` and `--isolate-for`. These are placeholders and can be renamed.

Out of scope for this change:
- Duplicate PLAY commands for Experiment B. PLAY messages don't go through the proxy yet, so that needs its own change.
- Restarting the coordinator automatically. Step 4 of Experiment C (coordinator crash and restart) stays a manual Ctrl+C and restart.

## Capabilities

### New Capabilities
- `chaos-proxy`: how the chaos proxy messes with traffic between speaker nodes and the coordinator. This change starts the spec with the timed isolation behavior.

### Modified Capabilities
- (none)

## Impact

- `src/chaos_proxy.py`: new switches, a saved start time, and a time-window check in the packet drop logic.
- No changes to `src/coordinator.py` or `src/speaker_node.py`.
- Experiment C can now run with one command line and no code edits:
  `python src/chaos_proxy.py --target-node NodeA --isolate-after 5 --isolate-for 10`
