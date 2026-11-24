# Tasks

## 1. Mark finished milestones

- [x] 1.1 In `docs/milestones.md`, add ` [DONE]` to the end of the seven `## Milestone 0` – `## Milestone 6` titles. Verify: searching for `[DONE]` finds exactly 7 lines, all of them milestone titles.

## 2. Fix M5 (clock drift)

- [x] 2.1 In the M5 "You will build" list, replace the `--drift-ppm` bullet with: drift is the 3rd plain argument in PPM, for example `python src/speaker_node.py NodeB 5004 50`. Verify: `--drift-ppm` no longer appears anywhere in `docs/milestones.md`, and the example matches `src/run_cluster.py:68`.
- [x] 2.2 In the same list, fix the clock formula bullet so it matches `get_drifted_time()` in `src/speaker_node.py`: start time + elapsed monotonic time × (1 + drift rate). Verify: compare the bullet side by side with `src/speaker_node.py:40-43`.

## 3. Fix M6 (rejoin)

- [x] 3.1 In the M6 "You will build" list, replace the "rejoin message sent by a node" bullet: the coordinator marks a node lost after 2.5s without a heartbeat, and when its heartbeat comes back it prints `Node X is back online!` and sends that node a `STATE_SNAPSHOT`. Keep the other two bullets. Verify: the word "rejoin message" is gone, and the text matches `src/coordinator.py:73-78` and `113-119`.

## 4. Add M7 (clock synchronization, planned)

- [x] 4.1 After M6 (before `## Anchor Experiments`), add `## Milestone 7 — Clock synchronization` with no `[DONE]`, in the same layout as the other milestones: **Concept** line, short intro, **You will build** (a node asks the coordinator for the time, measures the round trip, corrects its clock by reply time + half the round trip − its own time), **You will learn** (why sync is needed, how round-trip time is used, why uneven delay makes sync inaccurate, how this relates to NTP), **Experiment** (Error column before vs after sync; then add chaos proxy delay and see sync get worse), and a **Commit message** line `m7: ...`. Verify: M7 has the same headings as M5 and M6, and nothing in it claims the feature already exists.
- [x] 4.2 Check the M5 bullet "What NTP does conceptually (without implementing it)" still makes sense next to M7. If it does, leave it; if not, point it at M7 (e.g. "M7 builds a simple version"). Verify: M5 and M7 don't contradict each other.

## Workflow follow-up

- Archive the change once all tasks are checked (no specs to sync: `skip_specs: true`).
- Next change: build M7 (clock synchronization), with its own spec rules for `node-clock` and the coordinator.
