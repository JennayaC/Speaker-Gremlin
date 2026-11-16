# Tasks

## 1. PLAY goes through the chaos proxy

- [x] 1.1 In `src/chaos_proxy.py` main loop, right after the message is parsed, add a PLAY path: if `type` is `"PLAY"`, forward it to `('127.0.0.1', msg["to_port"])`, print `Relay PLAY to port <port>`, and `continue` so the heartbeat drop/delay/isolation code never sees it. Verify: read it and check the heartbeat code below is unchanged.
- [x] 1.2 In `src/coordinator.py` PLAY loop, add a `to_port` field for each node and send the PLAY to the proxy (`127.0.0.1:5002`) instead of the node port. Remove the commented-out "send duplicate" line. Verify: run `python src/run_cluster.py`; the proxy prints 3 `Relay PLAY` lines and each node prints `Received PLAY command` once.
- [x] 1.3 Check Experiments A and C still behave as before. Verify: `--experiment A` still shows `heartbeat lost` / `back online` for NodeA and NodeA still gets PLAY; `--experiment C` (coordinator in its own terminal) still loses NodeA around 7-8s and gets it back around 15s.

## 2. Duplicate mode

- [x] 2.1 In `src/chaos_proxy.py`, add a `--duplicate` switch (float, default 0.0, help text like `--drop`) and show it in the startup line. In the PLAY path, after relaying, send a second copy when `random.random() < args.duplicate` and print `Duplicate PLAY to port <port>`. Verify: run the proxy by hand with `--duplicate 1.0`, and the startup line shows it.
- [x] 2.2 Add `"B": {"proxy_args": ["--duplicate", "1.0"], "start_coordinator": True}` to the `EXPERIMENTS` dictionary in `src/run_cluster.py`, with a short comment like the A and C entries. Verify: `python src/run_cluster.py --experiment Z` lists A, B, C.
- [x] 2.3 Run `python src/run_cluster.py --experiment B`. Verify: the proxy prints `Relay` and `Duplicate` for each node, and each node prints `Received PLAY command` once and `Drop redundant PLAY command (seq 1). Last applied: 1` once.

## 3. Docs

- [ ] 3.1 In `docs/milestones.md` Experiment B, add a "How to run it" section (before Findings) with `python src/run_cluster.py --experiment B`, what to watch for (from 2.3), Ctrl+C to stop, and an optional "break it" step: comment out the `cmd_seq` check in `src/speaker_node.py` and run again to see the node react twice. Verify: following the steps as written gives the output from 2.3.
- [ ] 3.2 In `README.md` "Quick way", change the experiment line to mention `--experiment A`, `B`, or `C`. Verify: the names match the dictionary.

## Workflow follow-up

- Archive the change once all tasks are checked, and sync the chaos-proxy and cluster-launcher specs.
- Later change: send STATE_SNAPSHOT to every node when the coordinator shifts `target_play_time`.
- Later change: coordinator catches up to node versions after a restart.
