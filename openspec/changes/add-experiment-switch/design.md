# Design

## Context

`src/run_cluster.py` has a hardcoded `commands` list. Switching experiments means commenting lines in and out. The coordinator line is currently commented out (left over from Experiment C). The chaos proxy already has every switch A and C need (`--target-node`, `--max-delay`, `--wait-after`, `--isolate-for`), so only the launcher changes.

## Goals / Non-Goals

**Goals:**
- One command per experiment, no editing code.
- Adding a new experiment later (like B) means adding one dictionary entry.

**Non-Goals:**
- Experiment B, or any new chaos proxy behavior.
- Changing node names, ports, or drift values per experiment. All experiments use the same 3 nodes.

## Decisions

**1. A dictionary of experiments.** Near the top of `run_cluster.py`, a dictionary maps each name (`"A"`, `"C"`) to two things: the extra chaos proxy arguments, and whether to start the coordinator. A missing `--experiment` uses a "normal" entry (no proxy arguments, coordinator on).
- Why: all experiment setups sit in one place you can read at a glance.
- Alternative: an `if/elif` chain per name. Works, but grows messier with every experiment.

**2. Use `argparse` with `choices`.** `choices` comes from the dictionary's keys, so the valid names are always in sync with the dictionary. `argparse` prints the error and exits before anything starts, which covers the "unknown name" requirement for free. The chaos proxy already uses `argparse`, so it's the same tool.

**3. Build the `commands` list from the chosen entry.** Coordinator first (only if the entry says so), then the proxy with its arguments, then the 3 nodes. The startup loop, stagger, and shutdown code stay as they are.

**4. Default run includes the coordinator.** Matches the README "Quick way". Experiment C turns it off so you can restart the coordinator in its own terminal.

**5. Remove old commented-out lines.** The dictionary replaces them.

## Risks / Trade-offs

- [Typing `a` instead of `A` fails] → The error lists the valid names, so it's obvious. Could accept either case later if it gets annoying.
- [Someone forgets the coordinator in Experiment C] → The C "How to run it" steps in `docs/milestones.md` say to start it in Terminal 1 first. The launcher could also print a reminder line when the coordinator is off.
