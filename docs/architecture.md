# Speaker Gremlins — Architecture

> Living document. Updated as decisions are made. Each section notes
> *why* we made a choice, not just *what* we chose.

---

## Version 0 — Conceptual Model

This describes the architecture we are targeting for the first runnable version.
It will change. When it does, we note why.

---

### Components

```
┌──────────────────────────────────────────────────────────────┐
│                        MacBook (localhost)                    │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │ Speaker  │    │ Speaker  │    │ Speaker  │               │
│  │  Node A  │    │  Node B  │    │  Node C  │               │
│  │ :5001    │    │ :5002    │    │ :5003    │               │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘               │
│       │               │               │                      │
│       └───────────────┼───────────────┘                      │
│                       │                                      │
│               ┌───────┴────────┐                             │
│               │ Chaos Proxy    │  (optional, milestone 3+)   │
│               │ :6000          │                             │
│               └───────┬────────┘                             │
│                       │                                      │
│               ┌───────┴────────┐                             │
│               │  Coordinator   │                             │
│               │  :5000         │                             │
│               └────────────────┘                             │
│                                                              │
│  [Terminal observer reads stdout from all processes]         │
└──────────────────────────────────────────────────────────────┘
```

**Note**: The Chaos Proxy is introduced later. Early milestones will have nodes
talk directly to the coordinator. We add the proxy once we understand what we
want to intercept.

---

### Component responsibilities

#### Speaker Node
- Listens on a UDP port
- Receives commands (PLAY, PAUSE, SEEK, SYNC)
- Maintains local playback state: `{playing: bool, position: float, last_updated: timestamp}`
- Sends periodic heartbeats to coordinator
- Logs all received messages with timestamps

#### Coordinator
- Sends timed playback commands to all nodes
- Receives heartbeats and tracks which nodes are alive
- Detects silent nodes (failure detection)
- In early milestones: single point of authority
- Later: we will question whether this is the right model

#### Chaos Controller (proxy)
- Sits in the message path between coordinator and nodes
- Can: delay, drop, duplicate, or reorder messages
- Controlled via a simple config file or stdin commands
- Added in Milestone 3

#### Observer
- Not a separate process in early milestones
- Each node and coordinator prints structured log lines to stdout
- You run each process in its own terminal pane
- Format: `[NodeA][12.438s] recv PLAY seq=4 coordinator_ts=12.430s drift=+8ms`

---

### Message format (v0 — to be designed)

We have not defined the wire format yet. Key questions to answer:
- What fields does every message need?
- Should we use JSON (readable) or a binary struct (fast, compact)?
- What is the minimum information a PLAY command must carry?

These will be designed in Milestone 1.

---

## Decision log

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Separate OS processes, not objects | Real sockets, real timing, real packet behavior |
| 2 | Python for prototype | Fast iteration; focus on concepts not language |
| 3 | UDP over TCP (see `milestones.md`) | Exposes packet loss and ordering problems explicitly |
| 4 | No external frameworks initially | Must understand mechanics before abstracting them |
| 5 | Coordinator model (v0) | Simplest starting point; centralized vs. decentralized is an open question |
| 6 | Text/terminal observer | No dashboard needed; structured stdout teaches what to log |

---

## Open architectural questions

These are intentionally not answered yet. We will reach them through experiments.

1. **Centralized vs. decentralized**: Does a permanent coordinator make sense?
   What happens if the coordinator itself fails?

2. **Logical clocks vs. wall clocks**: Should nodes use `time.time()` (wall clock)
   or a logical counter for ordering? What are the tradeoffs?

3. **Pull vs. push for state sync**: Should nodes ask "what is the current state?"
   or should the coordinator broadcast it continuously?

4. **Idempotent commands**: If a PLAY command is delivered twice, should the node
   play twice, or ignore the duplicate? How does it know it's a duplicate?

5. **What does "synchronized" mean exactly?** ±5ms? ±100ms? How do we measure it?
