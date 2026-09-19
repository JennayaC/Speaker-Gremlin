# Speaker Gremlins

A distributed-systems learning experiment simulating independent networked speaker nodes over an unreliable network.

---

## What this is

Speaker Gremlins simulates a small cluster of independent networked "speaker" nodes that try to maintain synchronized playback state. A separate **Chaos Proxy** intentionally introduces network faults — dropping packets, injecting latency/jitter, simulating oscillator clock drift, and isolating nodes — to make distributed-systems failure modes **visible and tangible**.

The goal is not to build an audio player, but to observe, diagnose, and handle real distributed systems failures over actual OS sockets.

---

## What this is not

- Not a music player or audio DSP engine
- Not a Bluetooth / Wi-Fi audio engineering project
- Not a framework-heavy demo (built with zero dependencies using Python standard library)

---

## The Core Question

> When multiple independent processes try to agree on shared state over an unreliable network, what actually breaks, how do you detect it, and how do you recover?

---

## Key Concepts Demonstrated

- **Packet Loss Detection:** Nodes attach monotonically increasing sequence numbers (`seq`). The Coordinator detects dropped packets when sequence numbers jump (`seq > expected`).
- **Jitter & Out-of-Order Delivery:** Network delay variance is absorbed using absolute scheduled timestamps (`play_at`) rather than immediate execution commands.
- **Clock Drift:** Hardware oscillator variance is simulated in parts-per-million (`--drift-ppm`). Nodes calculate local timestamps that diverge from real time over duration.
- **Heartbeats & Failure Detection:** Nodes emit periodic heartbeats; silence exceeding the timeout threshold (2.5s) marks a node as dead.
- **State Snapshot Recovery:** When a disconnected or failed node rejoins, the Coordinator pushes a `STATE_SNAPSHOT` carrying the original `play_at` schedule, allowing the node to calculate elapsed time and snap into sync with active playback.

---

## Running the Cluster

The cluster consists of separate OS processes communicating over local UDP sockets. Open separate terminal windows or panes for each process:

### 1. Start the Coordinator
Listens for heartbeats, monitors health, and schedules playback:
```bash
python src/coordinator.py
```

### 2. Start the Chaos Proxy
Intercepts node traffic on port `5002`, injects jitter and packet drops, and forwards to coordinator port `5001`:
```bash
python src/chaos_proxy.py
```

### 3. Start Speaker Nodes
Launch 3 nodes with unique identifiers, listen ports, and simulated drift (PPM):

```bash
# Terminal 3: Node A (Zero drift)
python src/speaker_node.py NodeA 5003 0

# Terminal 4: Node B (+50 PPM faster clock)
python src/speaker_node.py NodeB 5004 50

# Terminal 5: Node C (-100 PPM slower clock)
python src/speaker_node.py NodeC 5005 -100
```

### 4. Observe Playback and Chaos
- Once all 3 nodes register, the Coordinator schedules a synchronized `PLAY` event 2 seconds in the future.
- Check the console logs: all nodes compute their individual wait times and trigger playback at the exact target timestamp.
- **Test Node Recovery:** Terminate `NodeA` with `Ctrl+C`. Observe the Coordinator declare `NodeA heartbeat lost` after 2.5s. Relaunch `NodeA` and observe the Coordinator issue a `STATE_SNAPSHOT` and `NodeA` snap forward to the current track position.

---

## Repository Structure

```
Speaker-Gremlin/
├── README.md           <- Project overview and running instructions
├── AGENTS.md           <- Learning guidelines and pair-programming rules
├── docs/
│   ├── architecture.md <- Living system design and wire protocol specs
│   ├── milestones.md   <- Milestone roadmap and anchor experiments
│   └── M0_plan.md      <- Milestone 0 bootstrap design
└── src/
    ├── coordinator.py  <- Cluster master, failure detector, and scheduler
    ├── chaos_proxy.py  <- Fault injection proxy (drop rate, latency jitter)
    └── speaker_node.py <- Speaker node process with simulated clock drift
```

---

## Git Philosophy

Each commit represents one learning milestone. The history reads like a lab notebook tracking iterative solutions to distributed problems.
