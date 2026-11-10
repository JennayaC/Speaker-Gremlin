# Tasks

## 1. The experiment switch in run_cluster.py

- [x] 1.1 In `src/run_cluster.py`, add a dictionary near the top (after the imports) with entries for normal, `A`, and `C`. Each entry holds the chaos proxy arguments and whether to start the coordinator. Verify: read it and check A = `--target-node NodeA --max-delay 3.5` with coordinator on, C = `--target-node NodeA --wait-after 5 --isolate-for 10` with coordinator off.
- [x] 1.2 Add an `argparse` parser with an optional `--experiment` switch whose `choices` come from the dictionary. Verify: `python src/run_cluster.py --experiment Z` prints an error listing A and C and starts nothing.
- [x] 1.3 Replace the hardcoded `commands` list with one built from the chosen entry (coordinator if on, then proxy with its arguments, then NodeA, NodeB, NodeC). Remove the old commented-out lines. Verify: the startup and shutdown code below it is unchanged.
- [ ] 1.4 Print which experiment is running at startup (and a reminder to start the coordinator yourself when it's off). Verify: the first lines of output name the experiment.

## 2. Check each setup runs

- [ ] 2.1 Run `python src/run_cluster.py`. Verify: the coordinator starts and sees all 3 nodes, no drops. Ctrl+C stops everything.
- [ ] 2.2 Run `python src/run_cluster.py --experiment A`. Verify: the coordinator shows NodeA heartbeats late or `heartbeat lost` for NodeA, like the Experiment A findings.
- [ ] 2.3 Start `python src/coordinator.py` in Terminal 1, then `python src/run_cluster.py --experiment C` in Terminal 2. Verify: NodeA is lost around 7-8s and back around 15s, and Ctrl+C in Terminal 2 does not stop the coordinator.

## 3. Docs

- [ ] 3.1 In `docs/milestones.md` Experiment C "How to run it", replace step 1 (commenting lines) with `python src/run_cluster.py --experiment C`. Verify: following the steps as written reproduces 2.3.
- [ ] 3.2 In `docs/milestones.md` Experiment A, add a short "How to run it" with `python src/run_cluster.py --experiment A`. Verify: the command matches 2.2.
- [ ] 3.3 In `README.md` "Quick way", add one line saying `--experiment A` or `--experiment C` runs an experiment setup. Verify: names match the dictionary.

## Workflow follow-up

- Archive the change once all tasks are checked.
- Later change: Experiment B (duplicate mode in the chaos proxy, and sending PLAY through the proxy).
