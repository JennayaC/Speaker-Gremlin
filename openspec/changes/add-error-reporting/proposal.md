# Proposal

## Why

When something breaks, it's hard to tell where. `run_cluster.py` prints five processes into one terminal, so a crash shows up as a long Python traceback mixed in with heartbeat lines, and most of the code sits in one big main loop, so "which function" usually just says `<module>`. Some problems are worse: they are never reported at all (the chaos proxy quietly treats an unreadable packet as a heartbeat and forwards it, which can then crash the coordinator). The user wants every error to say clearly which file, which node, and which part of the code it came from.

## What Changes

- **Crash line:** when the coordinator, chaos proxy, a speaker node, or the launcher crashes, it prints one short labelled line instead of the long traceback, e.g.
  `[speaker_node.py | NodeC | TIME_REPLY branch | line 141] CRASH: KeyError: 'coord_time'`
  It names the file, the node (speaker nodes only), the part of the code it was in, the line number, and the error. The process still stops, as it does today.
- **Parts of the code are named:** each process marks which step it is in (e.g. `startup`, `send heartbeat`, `PLAY branch`, `lost-node check`), so the crash line can say more than a line number.
- **Bad messages are reported, not crashed on or ignored:** when a process receives a message it can't read, or one that is missing a field it needs, it prints a labelled `WARNING` line and skips that message, then keeps running. Example:
  `[coordinator.py | heartbeat] WARNING: skipped message from NodeC, missing field(s): seq`
- **Chaos proxy behavior change:** an unreadable packet is now reported and dropped instead of being forwarded to the coordinator as if it were a heartbeat.
- **One small shared helper** (`src/error_report.py`) holds this logic so the four programs don't each repeat it.
- Normal print lines (heartbeats, PLAY, SYNC, etc.) do not change.

## Capabilities

### New Capabilities
- `error-reporting`: how every Speaker Gremlins process reports a crash (one labelled line naming file, node, part of the code, line, and error) and how it handles unreadable or incomplete messages (labelled warning, skip, keep running).

### Modified Capabilities
_None._ The existing `chaos-proxy`, `cluster-launcher`, and `node-clock` requirements don't describe error behavior; the unreadable-packet rule for the proxy is covered by `error-reporting`.

## Impact

- New file: `src/error_report.py`.
- Code: `src/coordinator.py`, `src/chaos_proxy.py`, `src/speaker_node.py`, `src/run_cluster.py` (step labels, message checks, using the helper).
- Depends on `add-clock-sync` being finished first: the message checks cover the new `TIME_REQUEST` / `TIME_REPLY` messages and the code they live in.
- Output: crashes look different (short line instead of a traceback). Normal output is unchanged.
- Out of scope: the launcher noticing that one of its child processes died, saving errors to a log file, and labelling every normal print line.
