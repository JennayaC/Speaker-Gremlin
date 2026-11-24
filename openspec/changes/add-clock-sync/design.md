# Design

## Context

See proposal.md for why. Current code facts that shape the approach:

- `src/speaker_node.py` reads positional args by index (`sys.argv[1..3]`); drift is optional `argv[3]`. `get_drifted_time()` (lines 40-43) is the only clock. Each loop: send heartbeat to the proxy (5002), then wait up to 0.5s for one incoming message. While waiting for `play_at` it `time.sleep()`s inside that loop.
- `src/coordinator.py` treats every packet as a heartbeat: it reads `msg['node']` and `msg['seq']` right away (lines 48-49), so a packet with no `seq` would crash it. Its truth clock is `time.time()`; the Error line is `(sender_ts - recv_time)`.
- `src/chaos_proxy.py` handles PLAY first (relay + `continue`), then treats everything else as a heartbeat (isolation, drop, delay via a background thread that forwards to the coordinator).
- `src/run_cluster.py` builds commands from an `EXPERIMENTS` dict with `proxy_args` and `start_coordinator`; node commands are hardcoded (lines 67-69).
- Nodes start with `start_real = time.time()`, so raw error starts at 0 and only grows from drift.

## Goals / Non-Goals

**Goals:**
- One run shows raw drift and synced drift for the same node on the same line.
- The sawtooth is visible: synced error creeps a little between syncs, then snaps back.
- With `--sync-delay`, the synced error jumps to roughly +half the delay, showing why uneven delay breaks the estimate.
- Every existing run (normal, A, B, C) prints and behaves exactly as now.

**Non-Goals:**
- Filtering bad samples (e.g. ignoring syncs with a long round trip). That's what real NTP adds; it's a nice follow-up experiment.
- Smoothly speeding up / slowing down the clock instead of jumping it.

## Decisions

**1. Two clocks in the node: raw and synced.**
Keep `get_drifted_time()` as the raw clock, untouched. Add a `clock_offset` (starts at 0) and a synced clock = raw + `clock_offset`. Everything that used `get_drifted_time()` for sending or scheduling switches to the synced clock. With sync off, `clock_offset` stays 0, so nothing changes.
*Alternative:* overwrite the raw clock on each sync. Rejected: then the original drift can't be shown any more.

**2. `--sync` is a plain flag, removed before reading positional args.**
Check whether `--sync` is in `sys.argv`, then read node/port/drift from the remaining args. This keeps `NodeB 5004 50` working and allows `NodeA 5003 --sync` (no drift).
*Alternative:* switch the node to argparse. Cleaner, but changes every existing command and the node-clock "Drift configuration" rule; not worth it here.

**3. New message pair, request through the proxy, reply direct.**
- `TIME_REQUEST` {type, node, port, t0} → proxy (5002) → coordinator.
- `TIME_REPLY` {type, t0, coord_time} → straight to the node's port.
The coordinator echoes `t0` back, so the node doesn't have to remember which request is outstanding (UDP can lose or reorder them).
Only the request goes through the proxy, the same path heartbeats take. That's what makes `--sync-delay` produce *uneven* delay, which is exactly what the experiment needs.
*Alternative:* piggyback on heartbeats (reply to every heartbeat). Rejected: mixes two ideas in one message, and heartbeat chaos (drop/delay) would then also hit sync, muddying Experiments A/C.

**4. Correction math (Cristian's algorithm), all in synced-clock time.**
```
t0 = synced clock when request sent        (carried in request, echoed back)
t1 = coordinator's time.time() when replying
t2 = synced clock when reply received
round_trip = t2 - t0
estimate   = t1 + round_trip / 2
correction = estimate - t2
clock_offset += correction
```
The node prints e.g. `[NodeC] SYNC: round trip 0.6ms, corrected clock by +49.8ms`.

**5. Sync every 5 seconds, counted in heartbeats.**
Heartbeats go out every ~0.5s, so "every 10th heartbeat" ≈ 5s. At −10000 PPM, NodeC drifts 50 ms in 5s: big enough to see the sawtooth, small next to raw error which reaches ~1s after 100s.

**6. Coordinator: time requests handled first, before heartbeat code.**
Right after parsing, if `type == "TIME_REQUEST"`, send the reply and skip the rest of the heartbeat handling for that packet. The lost-node check at the bottom of the loop still runs on the next loop, so a skipped packet doesn't hide a lost node.
Heartbeats with `raw_ts` print `[NodeC] Raw error: -312.0ms | Synced error: +0.4ms`; without it, the old line.

**7. Proxy: time requests get their own branch, like PLAY.**
After the PLAY branch, if `type == "TIME_REQUEST"`: if `--sync-delay` > 0, forward on a background thread after `random.uniform(0, sync_delay)`; otherwise forward now. Then `continue`, so heartbeat drop/delay/isolation never see it. The proxy says "time request" in its print lines, not "heartbeat".

**8. Launcher: experiments can set node drift and sync.**
Add two optional keys to an experiment entry: `drifts` (list of 3 PPM values, default `[0, 50, -100]`) and `sync` (default False). The node commands are built from these instead of being hardcoded. Normal/A/B/C don't set them, so they get today's values.
- `SYNC`: `proxy_args: []`, `start_coordinator: True`, `drifts: [0, 5000, -10000]`, `sync: True`
- `SYNC-DELAY`: same, `proxy_args: ["--sync-delay", "0.5"]`

## Risks / Trade-offs

- **[Node asleep when the reply arrives]** While waiting for `play_at` (up to 2s), the reply sits in the socket, so `t2` is late and one correction is wrong by up to ~1s. → The next sync 5s later fixes it. Mention it in the M7 notes as a real-world effect (busy devices make bad sync samples).
- **[Big drift vs. PLAY timing]** With sync on, NodeC's synced clock is at most ~50 ms off, so PLAY scheduling still works. → No special handling needed.
- **[Reply lost / coordinator down]** No reply, no correction; the node keeps its last offset and tries again in 5s. Windows `ConnectionResetError` is already caught in the node loop.
- **[Output volume]** Proxy prints a line per time request. → Acceptable; one per node every 5s.
