# Tasks

## 1. Node: two clocks and the `--sync` switch

- [x] 1.1 In `src/speaker_node.py`, at the argument parsing (top, lines 18-27): set a `sync_on` flag if `--sync` is in the arguments, and read node / port / drift from the arguments with `--sync` removed. Verify: `python src/speaker_node.py NodeB 5004 50` and `python src/speaker_node.py NodeA 5003 --sync` both start without an error (Ctrl+C to stop).
- [x] 1.2 Right after `get_drifted_time()`: add `clock_offset = 0.0` and a synced-clock function (raw + `clock_offset`). Switch every place that sends a timestamp or schedules (`sender_ts`, both `wait_time` lines, the "Local time" prints) to the synced clock. Verify: a normal `python src/run_cluster.py` run prints the same `Error` values as before (tiny, growing for NodeB/NodeC) and nodes still play.
- [x] 1.3 In the heartbeat message: add a `raw_ts` field (raw clock) only when `sync_on`. Verify: normal run still works; nothing visible changes yet.

## 2. Coordinator: time source and side-by-side errors

- [x] 2.1 In `src/coordinator.py`, right after `msg = json.loads(...)`, before `node = msg['node']`: if the message is a `TIME_REQUEST`, send a `TIME_REPLY` with the request's `t0` and `time.time()` straight to `('127.0.0.1', msg['port'])`, then skip the heartbeat code for this packet. Verify: normal run unchanged, no crash.
- [x] 2.2 At the "Clock Error (Drift)" print (line ~56-59): if the heartbeat has `raw_ts`, print `[Node] Raw error: ...ms | Synced error: ...ms` (both against `recv_time`); otherwise keep the old line. Verify: start coordinator, proxy, and `python src/speaker_node.py NodeC 5005 -10000 --sync` by hand; coordinator shows both columns for NodeC, and both grow (no correction yet).

## 3. Node: ask for the time and correct the clock

- [x] 3.1 In the node main loop, after sending the heartbeat: when `sync_on` and this is every 10th heartbeat, send a `TIME_REQUEST` {type, node, port, t0 = synced clock} to the proxy. Verify: with the same hand-started setup, the coordinator receives requests and does not crash (proxy currently forwards them as if heartbeats; fixed in 4.1).
- [x] 3.2 In the node's receive section, add a `TIME_REPLY` branch: compute round trip, estimate, correction (design.md decision 4), add it to `clock_offset`, and print `[NodeC] SYNC: round trip ...ms, corrected clock by ...ms`. Verify: NodeC prints a SYNC line about every 5s with a correction of about +50 ms; on the coordinator, NodeC's synced error stays within ~±50 ms (sawtooth) while raw error keeps growing.

## 4. Chaos proxy: time requests

- [x] 4.1 In `src/chaos_proxy.py`, after the PLAY branch: add a `TIME_REQUEST` branch that forwards to the coordinator, prints `Forward time request from <node>`, and `continue`s. Verify: hand-started run shows the new line, and `--target-node NodeC --drop 1.0` still lets NodeC's time requests through (heartbeats dropped, SYNC lines still appear).
- [x] 4.2 Add `--sync-delay` (float, default 0.0, help text like `--max-delay`) and show it in the startup line. In the time-request branch, when it's above 0, forward on a background thread after `random.uniform(0, sync_delay)` and print the delay. Verify: with `--sync-delay 0.5`, NodeC's synced error jumps around by up to roughly +250 ms after each sync; heartbeats still show "No delay or drop".

## 5. Launcher: SYNC and SYNC-DELAY setups

- [x] 5.1 In `src/run_cluster.py`: build the three node commands from optional experiment keys `drifts` (default `[0, 50, -100]`) and `sync` (default False, adds `--sync`), instead of the hardcoded lines 67-69. Update the comment above `EXPERIMENTS` to list the new keys. Verify: `python src/run_cluster.py --experiment A` still runs exactly as before.
- [x] 5.2 Add `"SYNC"` (`proxy_args: []`, coordinator on, `drifts: [0, 5000, -10000]`, `sync: True`) and `"SYNC-DELAY"` (same, `proxy_args: ["--sync-delay", "0.5"]`) with short comments like A/B/C. Verify: `--experiment Z` lists A, B, C, SYNC, SYNC-DELAY.
- [ ] 5.3 Run `--experiment SYNC` for ~30s and `--experiment SYNC-DELAY` for ~30s. Verify: SYNC shows raw error growing (NodeC about −300 ms after 30s) while synced error stays small; SYNC-DELAY shows synced error jumping to positive values (up to ~+250 ms) after syncs. Note the real numbers for the docs.

## 6. Docs

- [ ] 6.1 In `docs/milestones.md` M7: add `[DONE]` to the title, a "How to run it" section (SYNC, then SYNC-DELAY, what to look for from 5.3, Ctrl+C), and a short "Findings & Observations" with the real numbers from 5.3 (including the node-asleep risk from design.md if it showed up). Verify: following the steps gives the output described.
- [ ] 6.2 In `README.md` "Quick way": add `SYNC` and `SYNC-DELAY` to the experiment names. Verify: names match the `EXPERIMENTS` dictionary.

## Workflow follow-up

- Archive the change and sync the `clock-sync` (new), `node-clock`, `chaos-proxy`, and `cluster-launcher` specs.
- Possible later experiment: ignore sync samples with a long round trip (what real NTP does).
- Then continue the doc walkthrough: `architecture.md` (add TIME_REQUEST / TIME_REPLY), the report, the specs.
