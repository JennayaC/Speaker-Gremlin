# Tasks

These are steps for you to build yourself. Each one says how to check it worked.

## 1. Switches

- [ ] 1.1 In `src/chaos_proxy.py`, after the `--target-node` line (line 22), add `--isolate-after` and `--isolate-for` (both numbers in seconds, default 0). Check: `python src/chaos_proxy.py --help` lists both switches.
- [ ] 1.2 Add the isolation window to the "Chaos Proxy started" print line (line 28). Check: starting the proxy with `--isolate-after 5 --isolate-for 10` prints the window, and starting it with no switches still prints like before.

## 2. Time window check

- [ ] 2.1 Just before the main loop (line 40), save the proxy's start time using `time.monotonic()`. Check: the proxy still starts and forwards heartbeats like before.
- [ ] 2.2 Inside "3. Packet Drop Logic", before the random drop, check whether "now minus start time" is inside the window. If it is, print a drop message that says it's an isolation drop (not a random one) and skip the packet. Only do this when `--isolate-for` is more than 0. Check: with `--target-node NodeA --isolate-after 5 --isolate-for 10`, NodeA's heartbeats are forwarded for about 5s, dropped until about 15s, then forwarded again, and NodeB/NodeC are forwarded the whole time.

## 3. Run Experiment C

- [ ] 3.1 In `src/run_cluster.py`, add a commented-out proxy line for Experiment C (next to the existing testing line), using `--target-node NodeA --isolate-after 5 --isolate-for 10`. Check: switching to that line and running `python src/run_cluster.py` starts the cluster with no other code edits.
- [ ] 3.2 Run it and watch the coordinator. Check: you see "NodeA heartbeat lost" and the version bump around 7-8s, then "Node NodeA is back online!" around 15s, then NodeA prints the `CONFLICT ... Adopting coordinator version 2` line.
- [ ] 3.3 Step 4 by hand: with NodeA back, Ctrl+C the coordinator and start it again. Write down what NodeA does. Check: you have a note on whether NodeA accepted or rejected the restarted coordinator, and why.
- [ ] 3.4 Update Experiment C in `docs/milestones.md` so it gives the new command line instead of "isolate a node" by hand. Check: someone could follow the doc and repeat the experiment.
