# Speaker Gremlins — Architecture

> Living document. Updated as decisions are made. Each section notes
> *why* we made a choice, not just *what* we chose.

---

## Current Architecture (Milestones 0–6)

This describes the architecture implemented and tested across Milestones 0 through 6.

---

### Components & Topology

```
┌──────────────────────────────────────────────────────────────┐
│                        Local Host Cluster                    │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │ Speaker  │    │ Speaker  │    │ Speaker  │               │
│  │  Node A  │    │  Node B  │    │  Node C  │               │
│  │ :5003    │    │ :5004    │    │ :5005    │               │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘               │
│       │               │               │                      │
│       └───────────────┼───────────────┘                      │
│            HEARTBEAT  │ (uplink traffic)                     │
│                       ▼                                      │
│               ┌────────────────┐                             │
│               │  Chaos Proxy   │                             │
│               │  :5002         │                             │
│               └───────┬────────┘                             │
│       forwarded       │ (delayed / dropped)                  │
│       HEARTBEAT       ▼                                      │
│               ┌────────────────┐                             │
│               │  Coordinator   │                             │
│               │  :5001         │                             │
│               └───────┬────────┘                             │
│                       │                                      │
│                       │ PLAY / STATE_SNAPSHOT (downlink)     │
│                       └──────────────────────────────────────┘
│                                                              │
│  [Stdout from all processes serves as the distributed log]   │
└──────────────────────────────────────────────────────────────┘
```

**Network Routing:**
- **Uplink (Nodes $\to$ Chaos Proxy $\to$ Coordinator):** Nodes transmit periodic heartbeats to the Chaos Proxy on port `5002`. The proxy injects configurable drop rates and jitter delays before forwarding packets to the Coordinator on port `5001`.
- **Downlink (Coordinator $\to$ Nodes):** The Coordinator tracks each node's declared port (e.g. `5003`, `5004`, `5005`) and sends control messages (`PLAY`, `STATE_SNAPSHOT`) directly to the nodes.

---

### Component Responsibilities

#### Speaker Node (`src/speaker_node.py`)
- Binds to a designated UDP port (`sys.argv[2]`).
- Periodically transmits a `HEARTBEAT` message with sequence number, port, and drifted local timestamp.
- Simulates hardware oscillator error using a configurable drift rate (`--drift-ppm` / `sys.argv[3]`).
- Listens for coordinator control commands:
  - `PLAY`: Computes wait time until `play_at` timestamp and sleeps until execution time.
  - `STATE_SNAPSHOT`: Computes elapsed time since `play_at` and snaps directly to the current track position.

#### Coordinator (`src/coordinator.py`)
- Binds to UDP port `5001`.
- Ingests heartbeats, tracks membership (`detected_nodes`), and associates nodes with their listen ports (`node_ports`).
- Measures network/clock error: compares node timestamp against arrival time.
- Detects packet drops by tracking missing sequence numbers (`seq > expected`).
- Performs failure detection: marks a node as lost if no heartbeat is received within `2.5s`.
- When all 3 nodes are registered, broadcasts a scheduled `PLAY` command with a 2-second future target time (`time.time() + 2.0`).
- When a lost node resumes heartbeats, pushes a `STATE_SNAPSHOT` so the node can synchronize without restarting the cluster.

#### Chaos Proxy (`src/chaos_proxy.py`)
- Binds to UDP port `5002`.
- Intercepts node heartbeats and applies probabilistic chaos:
  - **Packet Loss:** Drops packets if random value is below drop threshold.
  - **Latency & Jitter:** Injects random delay (e.g., 0–300ms) before forwarding to the Coordinator (`:5001`).

#### Observer
- Distributed observability is maintained via structured standard output from each process.
- Each event displays node identifier, timestamp, sequence numbers, and measured error (e.g., `[NodeA] Expected: 1718000.120 | Local: 1718000.125 | Error: +5.0ms`).

---

### Message Format (Wire Protocol)

Messages are JSON-encoded strings over raw UDP datagrams.

#### 1. `HEARTBEAT` (Node $\to$ Proxy $\to$ Coordinator)
```json
{
  "type": "HEARTBEAT",
  "node": "NodeA",
  "seq": 14,
  "sender_ts": 1718000000.142,
  "port": 5003
}
```

#### 2. `PLAY` (Coordinator $\to$ Nodes)
```json
{
  "type": "PLAY",
  "sender_ts": 1718000002.500,
  "play_at": 1718000004.500
}
```

#### 3. `STATE_SNAPSHOT` (Coordinator $\to$ Recovering Node)
```json
{
  "type": "STATE_SNAPSHOT",
  "play_at": 1718000004.500,
  "playback_state": "PLAYING"
}
```

---

## Decision Log

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Separate OS processes, not objects | Real sockets, real timing, real packet behavior |
| 2 | Python for prototype | Fast iteration; focus on concepts not language |
| 3 | UDP over TCP | Exposes packet loss and ordering problems explicitly without kernel buffering / hidden retransmission |
| 4 | No external frameworks | Must understand mechanics before abstracting them |
| 5 | Coordinator model | Centralized authority simplifies initial membership and state distribution |
| 6 | Text/terminal observer | Structured stdout teaches log design without adding UI dependencies |
| 7 | Absolute timestamp scheduling (`play_at`) | Overcomes network jitter/latency variance by scheduling playback at a future point in time rather than instantaneous trigger |
| 8 | Monotonic baseline for clock drift | Simulates oscillator imperfections using `time.monotonic() * (1 + drift_rate)` applied to wall-clock references |
| 9 | State snapshot over message replay | When a node reconnects, coordinator transmits current snapshot state rather than replaying missed historical messages |
| 10 | Uplink chaos interception | Intercepting node-to-coordinator traffic tests failure detection and packet loss without complicating two-way NAT/port routing in the proxy |

---

## Architectural Insights & Answers

These questions were posed at the project start and answered through the milestone implementations:

1. **Centralized vs. decentralized:**
   - A centralized coordinator provides an authoritative clock and membership roster, making failure detection and scheduling straightforward. However, it represents a single point of failure (SPOF); if the coordinator crashes, all coordination ceases.

2. **Logical clocks vs. wall clocks:**
   - Wall clocks (with future timestamps) are essential for synchronizing external physical events (e.g. audio playback at a target time). However, local wall clocks drift (PPM variance), demonstrating that physical timestamps alone cannot guarantee synchronization without a clock-sync protocol (e.g., NTP/PTP).

3. **Pull vs. push for state sync:**
   - We adopted a reactive **push** model: the coordinator detects the reappearance of a lost node's heartbeat and immediately pushes a `STATE_SNAPSHOT`. This eliminates the need for nodes to implement request-retry loops.

4. **Idempotent commands:**
   - By including an absolute `play_at` timestamp in the snapshot rather than an incremental delta ("play for 5 seconds"), commands become naturally idempotent. A node receiving duplicate snapshots calculates `elapsed = now - play_at` and arrives at the exact same track position.

5. **What does "synchronized" mean?**
   - In distributed audio, synchronization means human-inaudible skew (typically $<5$ms). Without clock synchronization, clock drift (e.g. $\pm50$ PPM) accumulates drift of $\sim3$ms every minute, meaning nodes will quickly drift out of synchronization even if they started at the exact same millisecond.
