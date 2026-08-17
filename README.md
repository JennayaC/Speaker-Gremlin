# Speaker Gremlins

A distributed-systems learning experiment running entirely on one MacBook.

---

## What this is

Speaker Gremlins simulates a small cluster of independent networked "speaker" nodes
that try to maintain synchronized playback state. A separate **Chaos Controller**
intentionally breaks things — dropping packets, injecting latency, drifting clocks,
isolating nodes — so the interesting behavior is the failure, not the happy path.

The project is not trying to build a real audio product.
It is trying to make distributed-systems failure modes **visible and tangible**.

---

## What this is not

- Not a music player
- Not a Bluetooth or audio engineering project
- Not a polished full-stack application
- Not a portfolio demo

---

## The core question

> When multiple independent processes try to agree on shared state over an unreliable
> network, what actually breaks, how do you detect it, and how do you recover?

---

## Learning goals

This project is for someone who understands Python, sockets, and basic networking
coursework but wants hands-on intuition for:

- **Packet behavior** — what does a dropped or duplicated packet look like to a receiver?
- **Latency and jitter** — how does variable delay affect a system that expects predictable timing?
- **Clock drift** — what happens when two nodes count time differently?
- **Heartbeats and failure detection** — how long does it take to notice a silent node?
- **Message ordering** — what does an out-of-order message do to shared state?
- **Distributed state** — how do nodes agree on "what is the current playback position"?
- **Acknowledgements and retries** — when should you retry? When does retrying make it worse?
- **Node rejoin** — how does a node that was offline catch up?

---

## Architecture philosophy

Each speaker is a **separate OS process** communicating over real sockets.
This means real messages moving through a real network stack, not simulated
function calls inside one program.

The chaos layer sits between the nodes and intercepts traffic.

Observability is a first-class feature: every node emits structured diagnostic
output so you can watch disagreement, drift, and recovery in real time.

---

## Running

> Not yet implemented. See `docs/milestones.md` for the roadmap.

---

## Repository structure (will evolve)

```
speaker_gremlins/
├── README.md           <- you are here
├── docs/
│   ├── architecture.md <- living design document
│   └── milestones.md   <- roadmap and learning concepts per stage
└── ...                 <- code arrives after design review
```

Structure will grow organically. New directories are introduced only when
there is a concrete reason.

---

## Experiments (planned)

See `docs/milestones.md` for the three anchor experiments planned for this project.

---

## Git philosophy

Each commit represents one learning milestone. The history should read like
a lab notebook, not a product release.
