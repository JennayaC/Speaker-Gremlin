import socket
import time
import json
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

COOR_ADDR = ('127.0.0.1', 5002) #node will send packets to chaos proxy


seq = 0
node_id = sys.argv[1]

print(f"I'M ALIVE! Node: {node_id}\n")

while True:
    msg = {
        "type": "HEARTBEAT",
        "seq": seq,
        "sender_ts": time.time(),
        "node": node_id
    }

    payload = json.dumps(msg).encode()
    sock.sendto(payload, COOR_ADDR)

    seq += 1
    time.sleep(0.5)

sock.close()
print("\nDone.")








