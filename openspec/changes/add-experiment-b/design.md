# Design

## Context

- Nodes send heartbeats to the proxy (port 5002), and the proxy forwards them to the coordinator (port 5001). The proxy only knows one destination: the coordinator.
- The coordinator sends PLAY straight to each node port (5003-5005) from `node_ports`, which it learns from the `port` field in heartbeats. STATE_SNAPSHOT goes the same way.
- Nodes already reject a repeated PLAY: they check `cmd_seq <= last_applied_seq` before changing any state.
- All three processes share one host (`127.0.0.1`), so a port number is enough to find a node.

## Goals / Non-Goals

**Goals:**
- PLAY passes through the proxy so the proxy can copy it.
- Experiments A and C keep their current behavior and output.

**Non-Goals:**
- Routing STATE_SNAPSHOT through the proxy.
- Dropping or delaying PLAY (see proposal, option (a)).
- Any change to `src/speaker_node.py`.

## Decisions

**1. The PLAY message says where it's going (`to_port`).** The coordinator keeps its loop over `node_ports`, but each PLAY it builds gets a `to_port` field with that node's port, and it sends the PLAY to the proxy (`127.0.0.1:5002`) instead of to the node. The proxy forwards it to `('127.0.0.1', msg["to_port"])`.
- Why: the message itself carries the destination, so the proxy doesn't need to track anything. The node ignores the extra field.
- Alternative: the proxy learns node ports from heartbeats and broadcasts each PLAY to all of them. Simpler for the coordinator, but the proxy would need to keep state, and a PLAY couldn't be aimed at one node.

**2. The proxy tells messages apart by `type`.** At the top of the main loop, after parsing, a message with `type == "PLAY"` takes a separate path: relay to `to_port`, maybe send a second copy, then `continue`. Everything else (heartbeats) goes through the existing drop/delay/isolation code unchanged.
- Why: the heartbeat code isn't touched at all, which is how A and C stay safe.
- Alternative: check the sender's address (5001 = coordinator). It works, but `type` is clearer to read and doesn't depend on ports.

**3. `--duplicate` is a chance, like `--drop`.** `random.random() < args.duplicate` decides whether to send a second copy right after the first. Experiment B uses `1.0`, so it always duplicates, which makes the run repeatable.
- Alternative: an on/off flag. Simpler, but a chance lets you try "sometimes duplicated" later with no code change.

**4. The proxy prints what it does with PLAY.** One line per relay (`Relay PLAY to port 5003`), and one more when it duplicates (`Duplicate PLAY to port 5003`), so you can line up proxy output with node output.

**5. Experiment B is one more dictionary entry.** `"B": {"proxy_args": ["--duplicate", "1.0"], "start_coordinator": True}` in `src/run_cluster.py`. `choices` comes from the keys, so `B` becomes valid automatically.

**6. Remove the commented-out duplicate line** in the coordinator's PLAY loop. The proxy replaces it.

## Risks / Trade-offs

- [Proxy not running means no PLAY] → Before, PLAY skipped the proxy, so nodes got it even without one. Now it doesn't. `run_cluster.py` always starts the proxy, and nodes already need the proxy for heartbeats, so the coordinator wouldn't see 3 nodes (and wouldn't send PLAY) without it anyway.
- [Windows "nobody home" error] → If the proxy sends to a node port that isn't open, the next `recvfrom` can raise `ConnectionResetError`. The proxy already catches it and keeps going. Its message says "Coordinator not reachable", which won't be accurate in that case; the message could be made more general.
- [Node is asleep when the duplicate arrives] → After the first PLAY, the node calls `time.sleep` until play time (~2s). The duplicate waits in the socket buffer and is read afterwards, where the `cmd_seq` check drops it. Same result, it just prints a bit later.
