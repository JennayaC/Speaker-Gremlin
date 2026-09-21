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
playback_state = "IDLE"
last_applied_seq = 0
current_version = 0

try:
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
                current_version = msg.get("version", 1)
                #Ignore duplicate / stale commands
                if msg["cmd_seq"] <= last_applied_seq:
                    print(f"[{node_id}] Drop redundant PLAY command (seq {msg['cmd_seq']}). Last applied: {last_applied_seq}")
                    continue
                last_applied_seq = msg["cmd_seq"]   
                print(f"[{node_id}] Received PLAY command, scheduled for: {msg['play_at']}")
                wait_time = msg["play_at"] - get_drifted_time()
                if wait_time > 0:
                    time.sleep(wait_time)
                    print(f"[{node_id}] PLAYING NOW! Local time: {get_drifted_time():.3f}")
            if msg["type"] == "STATE_SNAPSHOT":
                incoming_version = msg.get("version", 1)
                # Compare local version with incoming snapshot version
                if incoming_version > current_version:
                    print(f"[{node_id}] CONFLICT: Local version {current_version} is stale! Adopting coordinator version {incoming_version}")
                    current_version = incoming_version
                    playback_state = "PLAYING"
                    wait_time = msg['play_at'] - get_drifted_time()
                    if wait_time < 0:
                        elapsed = -wait_time
                        print(f"[{node_id}] RESUMED PLAYBACK! Snapped to {elapsed:.2f}s into track. Local time: {get_drifted_time():.3f}")
                    else:
                        time.sleep(wait_time)
                        print(f"[{node_id}] PLAYING NOW AFTER RECOVERY! Local time: {get_drifted_time():.3f}")
                else:
                    print(f"[{node_id}] REJECTED SNAPSHOT: Local version {current_version} >= incoming version {incoming_version}")
        except socket.timeout:
            pass
except KeyboardInterrupt:
    print(f"\n[{node_id}] Stopped by user.")
finally:
    sock.close()
    print("Done.")








