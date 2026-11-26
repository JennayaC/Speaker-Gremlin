# Tasks

Start only after `add-clock-sync` is finished. Line numbers below are from that point and may shift; find places by the description.

Test helpers used below (run in a separate terminal while the target program is running):
- Send garbage: `python -c "import socket; socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(b'hello', ('127.0.0.1', PORT))"`
- Send a message with a missing field: same command with `b'{"type": "HEARTBEAT", "node": "NodeC"}'` (or another JSON text) instead of `b'hello'`

## 1. Shared helper and the coordinator

- [ ] 1.1 Create `src/error_report.py` with: a label (file name, optional node name) and a current step; `set_label(...)`, `set_step(...)`; a crash handler that prints `[label | step | line N] CRASH: Type: message` using the deepest frame inside `src/` (and the function name if it's not `<module>`), skips KeyboardInterrupt, and is installed as both `sys.excepthook` and `threading.excepthook`; `warn(text)` printing `[label | step] WARNING: text`; `missing_fields(msg, names)` returning the names not in `msg`. Verify: `python -c "import sys; sys.path.insert(0, 'src'); import error_report"` runs without error.
- [ ] 1.2 In `src/coordinator.py`: import the helper at the top, set the label `coordinator.py`, and set step names (`startup`, `receive`, `TIME_REQUEST branch`, `heartbeat`, `node recovery`, `send PLAY`, `lost-node check`) at the start of each section. Verify: start a coordinator, then start a second one → the second prints one `[coordinator.py | startup | line ...] CRASH: OSError: ...` line and no traceback. Ctrl+C on the first prints "stopped by user" and no CRASH.
- [ ] 1.3 In the coordinator's receive section: read JSON safely (warn + `continue` if unreadable), and at the top of the `TIME_REQUEST` branch and the heartbeat section check the needed fields (`t0`, `port` / `node`, `seq`, `sender_ts`) and warn + `continue` if any are missing. Verify: with the coordinator running, send garbage to port 5001 → WARNING, keeps running; send `{"type": "HEARTBEAT", "node": "NodeC"}` → WARNING naming `seq, sender_ts`, no Error line; a normal `python src/run_cluster.py` shows no WARNING or CRASH lines.
- [ ] 1.4 In `README.md`, add a short "When something goes wrong" section: what a `CRASH` line and a `WARNING` line look like and how to read the label (file | node | part of code | line). Verify: the examples match what 1.2 and 1.3 printed.

## 2. Chaos proxy

- [ ] 2.1 In `src/chaos_proxy.py`: import the helper, label `chaos_proxy.py`, step names (`startup`, `receive`, `PLAY branch`, `TIME_REQUEST branch`, `heartbeat chaos`; inside the delayed-send functions set nothing, the function name appears automatically). Verify: start two proxies → the second prints one labelled `startup` CRASH line.
- [ ] 2.2 Replace the "bad JSON becomes `msg = {}`" code: warn and `continue` instead (don't forward). In the PLAY branch, warn + `continue` if `to_port` is missing. Verify: with coordinator + proxy + one node running, send garbage to 5002 → proxy WARNING, coordinator prints nothing new for it, heartbeats keep flowing; send `{"type": "PLAY"}` to 5002 → WARNING naming `to_port`.

## 3. Speaker node

- [ ] 3.1 In `src/speaker_node.py`: import the helper with label `speaker_node.py` at the top, add the node name with `set_label` right after the arguments are read, and set step names (`startup`, `send heartbeat`, `send time request`, `receive`, `PLAY branch`, `STATE_SNAPSHOT branch`, `TIME_REPLY branch`). Verify: `python src/speaker_node.py NodeC` (no port) prints one `[speaker_node.py | startup | line ...] CRASH: IndexError: ...` line; starting two `NodeC 5005` nodes → the second prints a labelled `startup` CRASH naming NodeC.
- [ ] 3.2 In the node's receive section: read JSON safely, warn + `continue` if unreadable or `type` is missing; check fields at the top of each branch (PLAY: `cmd_seq`, `play_at`; STATE_SNAPSHOT: `play_at`; TIME_REPLY: `t0`, `coord_time`). Verify: with a node running, send garbage to its port → WARNING, keeps sending heartbeats; send `{"type": "TIME_REPLY", "t0": 0}` → WARNING naming `coord_time`, no SYNC line.

## 4. Launcher and full check

- [ ] 4.1 In `src/run_cluster.py`: import the helper, label `run_cluster.py`, step names (`startup`, `start processes`, `running`, `shutdown`). Verify: `python src/run_cluster.py --experiment A` runs as before; Ctrl+C prints no CRASH line.
- [ ] 4.2 Full check: run `python src/run_cluster.py` and `--experiment SYNC` for ~15s each. Verify: no CRASH or WARNING lines, and the output looks the same as before this change.

## Workflow follow-up

- Archive the change and sync the new `error-reporting` spec.
- Add the helper and the CRASH / WARNING lines to `docs/architecture.md` during the doc walkthrough.
- Possible later idea: have the launcher notice when one of its processes stops and say which one.
