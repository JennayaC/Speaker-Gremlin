# Speaker Gremlins — Milestone Roadmap

Each milestone is a single learning unit with one clear concept,
one observable behavior, and one commit.

---

## Milestone 0 — Skeleton and first message

**Concept: process boundaries and raw sockets**

Before anything interesting happens, you need two processes that can actually
talk to each other. This milestone is about getting the plumbing right.

**You will build:**
- A minimal coordinator process that sends one UDP message
- A minimal speaker node that receives it and prints it

**You will learn:**
- The difference between `SOCK_DGRAM` (UDP) and `SOCK_STREAM` (TCP)
- Why `bind()` matters for the receiver but not necessarily the sender
- What a "port" represents in terms of process addressing
- How to run two Python scripts at once and see them exchange a message

**Experiment:** Can you make the coordinator send 10 messages and have the node
print each one with its arrival timestamp?

**Commit message:** `m0: two processes exchange a UDP message`

---

## Milestone 1 — Structured messages and timestamps

**Concept: wire format design and latency measurement**

A raw string is not a protocol. This milestone introduces message structure
and asks: if both ends have a clock, can you measure how long a message took?

**You will build:**
- A message format with: `type`, `seq` (sequence number), `sender_ts` (when sent)
- A receiver that logs: `seq`, `sender_ts`, `recv_ts`, `delta`

**You will learn:**
- Why sequence numbers exist (ordering, deduplication)
- What "latency" means: the one-way delay between send and receive
- Why measuring latency with two clocks on two different machines is unreliable
  (and why it is still useful on a single machine)
- The difference between `time.time()` (wall clock) and `time.monotonic()` (no jumps)

**Key question before you implement:** What is the minimum set of fields every
message in this system needs? Think about it, then we discuss.

**Commit message:** `m1: add message structure, sequence numbers, and latency logging`

---

## Milestone 2 — Three nodes and heartbeats

**Concept: failure detection via heartbeat timeouts**

You cannot detect a missing node unless you expect to hear from it regularly.
This milestone introduces heartbeats — and the timeout that makes silence meaningful.

**You will build:**
- Three speaker node processes, each sending a heartbeat every N seconds
- A coordinator that tracks "last heard from" per node
- A coordinator that prints a warning when a node goes quiet

**You will learn:**
- What a heartbeat is and why it is a fundamental primitive in distributed systems
- The tradeoff between heartbeat frequency (fast detection vs. traffic)
- Why the timeout value is non-obvious: too short → false positives, too long → slow detection
- What "failure" means from the coordinator's perspective (hint: it cannot see the node directly)

**Experiment:** Kill one node process with Ctrl+C. How quickly does the coordinator notice?
Change the timeout and repeat. What is the right value?

**Commit message:** `m2: three nodes with heartbeats and failure detection`

---

## Milestone 3 — Chaos proxy and packet loss

**Concept: packet loss, observable unreliability**

Until now everything has worked perfectly. Now we deliberately break it.
The chaos proxy sits in the message path and randomly drops packets.

**You will build:**
- A simple UDP proxy process that forwards messages between coordinator and nodes
- The ability to configure a drop rate (e.g., 20% of messages are silently discarded)
- Sequence-number gap detection on the receiver side

**You will learn:**
- What a proxy is and why it is useful for network experimentation
- What "packet loss" looks like from the sender's and receiver's perspective
- How a receiver can detect a missing message using sequence numbers
- The difference between "I did not receive it" and "it was not sent" — you cannot tell from one side

**Experiment:** Set drop rate to 50%. Watch the sequence number gaps appear in the node log.
What does the node know? What does it not know?

**Commit message:** `m3: chaos proxy with configurable packet drop`

---

## Milestone 4 — Latency injection and jitter

**Concept: jitter, timing sensitivity, and out-of-order delivery**

Packet loss is one failure mode. Variable delay is subtler and often more damaging
to systems that depend on timing.

**You will build:**
- Chaos proxy gains the ability to delay messages by a random amount within a range
- Node logs show inter-arrival timing, not just sequence
- A PLAY command with a target timestamp: "start playing at T=12.430s"

**You will learn:**
- What jitter is: variance in delivery delay, not just the delay itself
- Why a system that expects 50ms delivery can be broken by a message arriving at 200ms
  even if no messages are dropped
- What it means for a playback command to carry an absolute timestamp vs. "play now"
- How out-of-order delivery is possible without any packet loss

**Experiment:** With no packet loss but high jitter (0–300ms random delay),
observe whether nodes all start playing at the same perceived moment.

**Commit message:** `m4: latency injection and jitter; timestamped PLAY command`

---

## Milestone 5 — Clock drift simulation

**Concept: local clocks are not synchronized; drift accumulates**

Real devices do not share a clock. Each has its own oscillator that runs at
a slightly different rate. Over time, clocks that started together diverge.

**You will build:**
- Each node process accepts a `--drift-ppm` argument (parts per million)
- The node's local clock is simulated as `time.monotonic() * (1 + drift_rate)`
- The observer output now shows: `expected_ts | local_ts | error`

**You will learn:**
- What clock drift is and why it is measured in PPM
- Why distributed systems cannot rely on wall clocks without a synchronization protocol
- What NTP does conceptually (without implementing it)
- How synchronization error grows linearly with drift rate and time

**Experiment:** Run three nodes with drift values of 0, +50ppm, -100ppm.
After 60 seconds, how far apart are their clocks? Can you predict the answer
mathematically before running the experiment?

**Commit message:** `m5: simulated clock drift per node; drift visible in observer`

---

## Milestone 6 — Node rejoin and state recovery

**Concept: how does a returning node catch up?**

A node was isolated (you killed it or the chaos proxy blocked its traffic).
Now it comes back. What does it know? What does it not know? How does it recover?

**You will build:**
- A "rejoin" message sent by a node when it reconnects
- A coordinator response containing current playback state
- A node that applies the recovered state and resumes

**You will learn:**
- The rejoin problem: a returning node's last known state is stale
- Why "just replay all missed messages" can be expensive or impossible
- What "state snapshot" means vs. "message log" (two approaches to recovery)
- Why idempotency matters: if a node receives a message it already processed, what happens?

**Experiment:** Disconnect a node mid-playback using the chaos proxy.
Wait 10 seconds. Reconnect it. Does it recover gracefully? Does it snap to the
correct position or drift to it gradually?

**Commit message:** `m6: node rejoin with state snapshot recovery`

---

## Anchor Experiments

These are the three standalone experiments planned for later in the project.
Each one asks a specific engineering question.

---

### Experiment A — The Silence Problem

> **Question:** Can the coordinator distinguish a dead node from a slow node?

Set up one node with very high jitter (1–3 second delays) and one node that is
actually dead (process killed). From the coordinator's perspective, both nodes
go quiet. How do you tell the difference? What happens if you treat a slow node
as dead and send it a "rejoin" state snapshot?

This experiment surfaces the fundamental tension in failure detection: act too
fast → false positives; act too slow → real failures go undetected.

---

### Experiment B — The Duplicate Command Problem

> **Question:** What happens when the same PLAY command arrives twice?

Use the chaos proxy's duplicate mode to resend PLAY commands. If nodes are not
protected against duplicates, they will react twice. Design and implement an
idempotency mechanism (sequence numbers, or a "last applied seq" field) and
verify it handles duplicates correctly. Then deliberately break it to observe
what goes wrong.

This experiment teaches idempotency, at-most-once vs. at-least-once delivery,
and why these properties are hard to guarantee across a network.

---

### Experiment C — The Returning Stranger

> **Question:** A node rejoins with a conflicting view of the world. Who wins?

Isolate a node. While it is isolated, update the coordinator state (seek to a
new position, change playback speed, etc.). When the isolated node reconnects,
it carries stale state. Design a conflict resolution rule. Does the coordinator
always win? What if the coordinator itself crashed and was replaced?

This experiment is a direct entry point into consensus problems. You do not need
to implement Raft. But after this experiment you will understand intuitively why
Raft exists.

---

## What we are deliberately not building (yet)

- No leader election
- No Raft, Paxos, or any consensus protocol
- No distributed database
- No authentication
- No production-quality retries or exponential backoff
- No audio

These are not scope decisions. They are ordering decisions.
You can add them once you understand the problems they solve.
