import socket
import random
import time
import argparse
import json

# Define CLI arguments
parser = argparse.ArgumentParser(description="Chaos Proxy for Speaker Gremlins")
parser.add_argument("--drop", type=float, default=0.0, help="Probability of dropping packets (0.0 to 1.0)")
parser.add_argument("--max-delay", type=float, default=0.0, help="Maximum random delay in seconds")
parser.add_argument("--target-node", type=str, default=None, help="Target specific node (e.g. NodeA). Defaults to ALL.")
args = parser.parse_args()

print(f"Chaos Proxy started (Drop: {args.drop*100:.0f}%, Max Delay: {args.max_delay*1000:.0f}ms, Target: {args.target_node or 'ALL'})")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 5002))

try:
    while True:
        data, addr = sock.recvfrom(2048)
        try:
            msg = json.loads(data.decode())
            node = msg.get("node")
        except Exception:
            node = None

        # Check if this packet is targeted for chaos
        is_target = (args.target_node is None) or (node == args.target_node)

        if is_target:
            # Packet drop check
            if args.drop > 0 and random.random() < args.drop:
                print(f"Drop heartbeat from {node or addr}")
                continue

            # Jitter / delay check
            if args.max_delay > 0:
                delay = random.uniform(0, args.max_delay)
                time.sleep(delay)
                print(f"Forward heartbeat from {node or addr} (Delay: {delay * 1000:.1f}ms)")
            else:
                print(f"Forward heartbeat from {node or addr} (No delay or drop)")
        else:
            print(f"Forward heartbeat from {node or addr} (Passthrough)")

        sock.sendto(data, ('127.0.0.1', 5001))
except KeyboardInterrupt:
    print("\nChaos proxy stopped by user.")
finally:
    sock.close()
    print("Done.")
