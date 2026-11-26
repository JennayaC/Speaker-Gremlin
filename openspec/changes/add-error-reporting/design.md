# Design

## Context

See proposal.md for why. Code facts that shape the approach (as of `add-clock-sync` being finished):

- All four programs are scripts run as `python src/<name>.py`, so `src/` is on Python's import path and they can share a small helper module.
- Almost all logic is at module level inside one `while True` loop, not in functions. A traceback for most errors says `<module>`, which is why the crash label needs a hand-set "part of the code" name.
- Every main loop already has `except KeyboardInterrupt` and a `finally` that closes the socket and prints `Done.`.
- Message handling today:
  - `coordinator.py`: `json.loads` with no guard; reads `msg['node']`, `msg['seq']`, `msg['sender_ts']`, `msg["t0"]`, `msg["port"]` directly → any bad packet crashes it.
  - `chaos_proxy.py`: bad JSON is caught and turned into `msg = {}`, then forwarded to the coordinator as a heartbeat. PLAY reads `msg["to_port"]` directly.
  - `speaker_node.py`: `json.loads` with no guard; `msg["type"]`, `cmd_seq`, `play_at`, `t0`, `coord_time` read directly.
- The proxy forwards delayed heartbeats and delayed time requests on background threads.

## Goals / Non-Goals

**Goals:**
- One readable line per crash that points at the right file, node, part of the code, and line.
- Bad or incomplete packets never crash a process and are never silently ignored.
- Each program only gains a few short lines; the rules live in one place.

**Non-Goals:**
- Recovering from crashes (the process still stops).
- The launcher watching its child processes (each child already prints its own labelled crash line into the same terminal).
- Checking value *types* (e.g. `seq` being a string). Only "can't read it" and "field missing" are checked.

## Decisions

**1. One shared helper: `src/error_report.py`.**
It holds: the current label and step, a crash handler, a warning printer, and a missing-field checker. Each program imports it at the top.
*Alternative:* copy a few lines into each file. Rejected: four copies drift apart, and the label format must match everywhere.

**2. Catch crashes with Python's crash hook (`sys.excepthook`), not a giant `try` around everything.**
`sys.excepthook` is the function Python calls for any error nobody caught, including errors during startup (before the main loop, e.g. port already in use). The helper replaces it with one that prints the labelled line. The existing `try / except KeyboardInterrupt / finally` stays as is, so Ctrl+C still prints "stopped by user" and `finally` still closes the socket; the hook runs after that. The same handler is also set as `threading.excepthook`, so a crash in one of the proxy's background threads gets a label too (that thread stops; the proxy keeps running).
*Alternative:* wrap each whole script in `try / except Exception`. Rejected: needs re-indenting entire files and is easy to get wrong.

**3. "Part of the code" is a step name set by hand.**
Programs call a helper like `set_step("TIME_REPLY branch")` at the start of each section. Suggested names:
- coordinator: `startup`, `receive`, `TIME_REQUEST branch`, `heartbeat`, `node recovery`, `send PLAY`, `lost-node check`
- chaos proxy: `startup`, `receive`, `PLAY branch`, `TIME_REQUEST branch`, `heartbeat chaos`, plus the delayed-send functions
- speaker node: `startup`, `send heartbeat`, `send time request`, `receive`, `PLAY branch`, `STATE_SNAPSHOT branch`, `TIME_REPLY branch`
- launcher: `startup`, `start processes`, `running`, `shutdown`
*Alternative:* move each branch into its own function so the traceback names it. Rejected: big restructuring of working code, and it changes how the whole project reads.

**4. Line number = deepest frame in our own `src/` file.**
The handler walks the traceback and picks the last frame whose file is inside `src/`. That's the line in *our* code, even when the error was raised inside a library (`json`, `socket`). If that frame is inside a function (not `<module>`), the function name is added: `... | send heartbeat | get_drifted_time() line 47]`.

**5. Label format.**
`[<file> | <node, nodes only> | <step> | line N] CRASH: <ErrorType>: <message>`
`[<file> | <node> | <step>] WARNING: <what was skipped and why>`
The speaker node starts with label `speaker_node.py` and adds its node name right after the arguments are read (helper call like `set_label("speaker_node.py", node_id)`), so a crash in argument reading still gets a label.

**6. Short line only, no full traceback.**
With five processes in one terminal, the traceback is what makes crashes hard to read. The file + step + line is enough to find the problem in files this size.
*Alternative:* print the traceback and then the short line. Rejected for now; easy to add back later if needed.

**7. Message checks: read safely, check fields per type, `continue` on failure.**
- Right after `recvfrom`: parse JSON inside `try`; on failure print `WARNING: skipped unreadable message` and `continue`.
- At the top of each branch: ask the helper which of the needed fields are missing; if any, print a warning naming them and `continue`, before any state changes.
- Needed fields per type:
  - coordinator `TIME_REQUEST`: `t0`, `port`; heartbeat: `node`, `seq`, `sender_ts` (`port` stays optional, as today)
  - proxy PLAY: `to_port` (heartbeats and time requests only need to be readable; their `node` stays optional, as today)
  - node: `type`; PLAY: `cmd_seq`, `play_at`; STATE_SNAPSHOT: `play_at`; TIME_REPLY: `t0`, `coord_time`
- Proxy: an unreadable packet is no longer forwarded (it would only crash the coordinator).

## Risks / Trade-offs

- **[Forgot to update a step name]** A crash label could name the previous section. → The line number is always exact, so the problem can still be found; the step is a helpful hint, not the source of truth.
- **[Full traceback hidden]** For a deep call chain, only the deepest own line is shown. → Fine for this project's size (one level of functions at most).
- **[`continue` in the node loop skips the rest of that pass]** Same as the existing duplicate-PLAY `continue`: the next loop sends the next heartbeat normally. → No extra handling.
- **[Crash in a proxy thread]** That one delayed packet is lost; the proxy keeps running. → Labelled line makes it visible.

## Migration Plan

Apply after `add-clock-sync` is done and archived. No rollback steps needed beyond reverting the commit; no data or message formats change.
