
"""
Speaker Gremlins -- Cluster

- Allows all processes to run simultaneously and in the correct order. All in one terminal.

"""

import argparse
import subprocess
import sys
import time

# Setup used when no --experiment is given: everything runs, nothing is broken.
NORMAL = {"proxy_args": [], "start_coordinator": True}

# Named experiment setups. Each one says:
#   proxy_args        -> extra switches passed to the chaos proxy
#   start_coordinator -> start the coordinator with the cluster or not
EXPERIMENTS = {
    # Experiment A: NodeA is alive but very unreliable. 70% of its heartbeats are
    # dropped and the rest are delayed by up to 3.5s. Delay alone isn't enough:
    # some heartbeat almost always slips through within 2.5s, so the coordinator
    # never declares NodeA lost. The drops create gaps long enough to fool it.
    "A": {
        "proxy_args": ["--target-node", "NodeA", "--max-delay", "3.5", "--drop", "0.7"],
        "start_coordinator": True,
    },
    # Experiment B: the proxy sends every PLAY command twice.
    # Nodes should apply the first one and drop the copy (same cmd_seq).
    "B": {
        "proxy_args": ["--duplicate", "1.0"],
        "start_coordinator": True,
    },
    # Experiment C: cut NodeA off from 5s to 15s.
    # Coordinator is off so you can run (and restart) it in its own terminal.
    "C": {
        "proxy_args": ["--target-node", "NodeA", "--wait-after", "5", "--isolate-for", "10"],
        "start_coordinator": False,  # False = you must start the coordinator yourself in its own terminal
    },
}

# --experiment switch. Valid names come straight from the EXPERIMENTS keys,
# so adding a new experiment above automatically makes it a valid choice.
parser = argparse.ArgumentParser(description="Start the Speaker Gremlins cluster")
parser.add_argument("--experiment", choices=EXPERIMENTS.keys(), default=None,
                    help="Run a named experiment setup. Leave out for a normal run.")
args = parser.parse_args()

# Pick the setup: NORMAL if no --experiment was given, otherwise that experiment.
if args.experiment is None:
    setup = NORMAL
else:
    setup = EXPERIMENTS[args.experiment]

# Build the list of processes to start, in order.
commands = []

# 1. Coordinator first (only if this setup starts it)
if setup["start_coordinator"]:
    commands.append([sys.executable, "src/coordinator.py"])

# 2. Chaos proxy, with this setup's switches added on the end
commands.append([sys.executable, "src/chaos_proxy.py"] + setup["proxy_args"])

# 3. The three speaker nodes (same in every setup)
commands.append([sys.executable, "src/speaker_node.py", "NodeA", "5003", "0"])
commands.append([sys.executable, "src/speaker_node.py", "NodeB", "5004", "50"])
commands.append([sys.executable, "src/speaker_node.py", "NodeC", "5005", "-100"])

processes = []

try:
    # 1. Begin startup to allow enough time for ports to bind
    print("Starting Speaker Gremlins cluster...")
    if args.experiment is None:
        print("Setup: normal run (no experiment)")
    else:
        print(f"Setup: Experiment {args.experiment}")
    if not setup["start_coordinator"]:
        print("Coordinator NOT started. Start it yourself in its own terminal: python src/coordinator.py")
        # Wait here so the reminder can't scroll away, and so the proxy's
        # isolation timer only starts once the coordinator is really running.
        input("Press Enter once the coordinator is running...")
    for cmd in commands:
        p = subprocess.Popen(cmd)
        processes.append(p)
        time.sleep(0.2)  # brief stagger to let listening sockets bind

    # 2. Begin main loop to keep program running until user intervention
    print("\nAll cluster processes are running. Press Ctrl+C to stop the cluster.\n")
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nShutting down cluster...")
finally:
    for p in processes:
        p.terminate()
        p.wait()
    print("All processes stopped.")
