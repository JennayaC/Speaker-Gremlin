"""
Speaker Gremlins -- Chaos Proxy

- Sits between coordinator and speaker nodes
- Relays UDP packets
- Can drop packets or add delay
- Helps simulate network failures

"""

import socket
import random
import time
import argparse
import json
import threading 

# Define CLI arguments
parser = argparse.ArgumentParser(description="Chaos Proxy for Speaker Gremlins")
parser.add_argument("--drop", type=float, default=0.0, help="Probability of dropping packets (0.0 to 1.0)")
parser.add_argument("--max-delay", type=float, default=0.0, help="Maximum random delay in seconds")
parser.add_argument("--target-node", type=str, default=None, help="Target specific node (e.g. NodeA). Defaults to ALL.")
args = parser.parse_args()

PROXY_PORT = 5002
COORDINATOR_ADDR = ('127.0.0.1', 5001)

print(f"Chaos Proxy started (Drop: {args.drop*100:.0f}%, Max Delay: {args.max_delay*1000:.0f}ms, Target: {args.target_node or 'ALL'})")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', PROXY_PORT))

#Helper function so delay runs in background process without blocking incoming messages
def delayed_send(data, delay, node):
    time.sleep(delay)
    sock.sendto(data, COORDINATOR_ADDR) #forward to coordinator
    print(f"Forward heartbeat from {node} (Delay: {delay * 1000:.1f}ms)")

#Main loop
try:
    while True:
        # 1. Parse Packet to identify source node
        data, addr = sock.recvfrom(2048)
        try:
            msg = json.loads(data.decode())
            node = msg.get("node")
        except Exception:
            node = None

        # 2. Check if packet is targeted for chaos 
        is_target = (args.target_node is None) or (node == args.target_node)

        # 3. Packet Drop Logic
        if is_target:
            if args.drop > 0 and random.random() < args.drop:
                print(f"Drop heartbeat from {node or addr}")
                continue

            # 4. Jitter / delay check
            if args.max_delay > 0:
                delay = random.uniform(0, args.max_delay)
                threading.Thread(target=delayed_send, args=(data,delay,node), daemon=True).start()
                continue #jump to next packet after to continue recieving packets from other nodes
            else:
                print(f"Forward heartbeat from {node or addr} (No delay or drop)")
        else:
            print(f"Forward heartbeat from {node or addr} (Passthrough)")
            
        # 5. Forwarded Packet to Coordinator
        sock.sendto(data, COORDINATOR_ADDR)
except KeyboardInterrupt:
    print("\nChaos proxy stopped by user.")
finally:
    sock.close()
    print("Done.")
