import subprocess
import sys
import time

commands = [
    [sys.executable, "src/coordinator.py"],
    [sys.executable, "src/chaos_proxy.py", "--max-delay", "3.5", "--target-node", "NodeA"],
    [sys.executable, "src/speaker_node.py", "NodeA", "5003", "0"],
    [sys.executable, "src/speaker_node.py", "NodeB", "5004", "50"],
    [sys.executable, "src/speaker_node.py", "NodeC", "5005", "-100"],

]

processes = []

try:
    print("Starting Speaker Gremlins cluster...")
    for cmd in commands:
        p = subprocess.Popen(cmd)
        processes.append(p)
        time.sleep(0.2)  # brief stagger to let listening sockets bind

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
