import socket
import time
import json
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

COOR_ADDR = ('127.0.0.1', 5002) #node will send packets to chaos proxy


seq = 0
node_id = sys.argv[1]
port_num = int(sys.argv[2])
sock.bind(('127.0.0.1',port_num))
sock.settimeout(0.5)

if len(sys.argv) > 3:
    drift_val = float(sys.argv[3])
    drift_rate = drift_val/1e6
else:
    drift_rate = 0.0

start_real = time.time()
start_mono = time.monotonic()

def get_drifted_time():
    elapsed = time.monotonic() - start_mono
    drift = elapsed * (1.0 + drift_rate)
    return start_real + drift #this is the drifted wall time

print(f"I'M ALIVE! Node: {node_id}\n")

while True:
    msg = {
        "type": "HEARTBEAT",
        "seq": seq,
        "sender_ts": get_drifted_time(),
        "node": node_id,
        "port": port_num
    }

    payload = json.dumps(msg).encode()
    sock.sendto(payload, COOR_ADDR)

    seq += 1
    try:
        data, addr = sock.recvfrom(2048)
        msg = json.loads(data.decode())
        if msg["type"] == "PLAY":
            print(f"Received PLAY command, scheduled for: {msg['play_at']}")
            wait_time = msg["play_at"] - get_drifted_time()
            if wait_time > 0:
                time.sleep(wait_time)
                print(f"[{node_id}] PLAYING NOW! Local time: {get_drifted_time():.3f}")
    except socket.timeout:
        pass

sock.close()
print("\nDone.")








