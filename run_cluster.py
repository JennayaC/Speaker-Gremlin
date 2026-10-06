
"""
Speaker Gremlins -- Cluster

- Allows all processes to run simultaneously and in the correct order. All in one terminal.

"""

import subprocess
import sys
import time

commands = [
    [sys.executable, "src/coordinator.py"],
    #[sys.executable, "src/chaos_proxy.py", "--drop", "0.85", "--target-node", "NodeA"], (from testing keep commented for now)
    [sys.executable, "src/chaos_proxy.py"],
    [sys.executable, "src/speaker_node.py", "NodeA", "5003", "0"],
    [sys.executable, "src/speaker_node.py", "NodeB", "5004", "50"],
    [sys.executable, "src/speaker_node.py", "NodeC", "5005", "-100"],

]

processes = []

try:
    # 1. Begin startup to allow enough time for ports to bind
    print("Starting Speaker Gremlins cluster...")
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
