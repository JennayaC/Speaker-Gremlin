"""
Speaker Gremlins - Speaker Node

This node sends heartbeat messages to the chaos proxy and plays audio at the scheduled time.
- Receives playback commands from coordinator
- Waits until the scheduled time to play audio
- Detects clock drift and adjusts playback time
- Re-syncs with the cluster if it misses a command
-Enforces idempotency of PLAY commands (ignores duplicates)
-Updates its current state using state snapshots from the coordinator

"""
import socket
import time
import json
import sys

#CLI Argument Parsing - Node ID (1,2,3), Port Number (5003,5004,5005), Drift Value (+ or -)
#Optional --sync switch (Milestone 7): turns on clock sync with the coordinator.
#It can go anywhere, so remove it first and read the normal arguments from what's left.
sync_on = "--sync" in sys.argv
cli_args = [arg for arg in sys.argv if arg != "--sync"]

node_id = cli_args[1]
port_num = int(cli_args[2])

#Optional drift value for clock skew (in microseconds)
if len(cli_args) > 3:
    drift_val = float(cli_args[3])
    drift_rate = drift_val/1e6
else:
    drift_rate = 0.0

#Socket setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
COOR_ADDR = ('127.0.0.1', 5002) #node will send packets to chaos proxy
sock.bind(('127.0.0.1',port_num))
sock.settimeout(0.5)

#Starting clock values
start_real = time.time()
start_mono = time.monotonic()

#Uses monotonic timer to simulate a real hardware clock that drifts over time 
def get_drifted_time():
    elapsed = time.monotonic() - start_mono
    drift = elapsed * (1.0 + drift_rate)
    return start_real + drift #this is the drifted wall time

#Milestone 7: the synced clock = raw drifting clock + corrections from syncing.
#clock_offset stays 0 when sync is off, so the synced clock equals the raw clock.
#The raw clock is never changed, so the original drift can still be shown.
clock_offset = 0.0

def get_synced_time():
    return get_drifted_time() + clock_offset

print(f"I'M ALIVE! Node: {node_id}\n")

#Variables to keep track of node state
seq = 0 #Outgoing heartbeat sequence number
playback_state = "IDLE" #Current state of the node
last_applied_seq = 0 #Sequence number of last applied PLAY command
current_version = 0 #Version number of last applied state snapshot

#Main loop
try:
    while True:
        msg = {
            "type": "HEARTBEAT",
            "seq": seq,
            "sender_ts": get_synced_time(),
            "node": node_id,
            "port": port_num
        }
        #Milestone 7: with sync on, also send the raw drifting clock so the coordinator can show the original drift next to the synced clock.
        if sync_on:
            msg["raw_ts"] = get_drifted_time()

        payload = json.dumps(msg).encode()
        sock.sendto(payload, COOR_ADDR)

        #Milestone 7: every 10th heartbeat (about every 5s), ask the coordinator for the time.
        #t0 = our synced clock right now. The coordinator sends it back, so we canmeasure the round trip when the reply arrives.
        if sync_on and seq % 10 == 0:
            time_req = {
                "type": "TIME_REQUEST",
                "node": node_id,
                "port": port_num,
                "t0": get_synced_time()
            }
            sock.sendto(json.dumps(time_req).encode(), COOR_ADDR)

        seq += 1
        try:
            data, addr = sock.recvfrom(2048)
            msg = json.loads(data.decode())

            # 1. Handle PLAY Command (idempotency check)
            if msg["type"] == "PLAY":
                incoming_version = msg.get("version", 1)
                #Ignore duplicate / stale commands (check BEFORE changing any state)
                if msg["cmd_seq"] <= last_applied_seq:
                    print(f"[{node_id}] Drop redundant PLAY command (seq {msg['cmd_seq']}). Last applied: {last_applied_seq}")
                    continue
                #Reject commands from an older state version (same rule as STATE_SNAPSHOT, never downgrade)
                if incoming_version < current_version:
                    print(f"[{node_id}] REJECTED PLAY: Local version {current_version} > incoming version {incoming_version}")
                    continue
                #Command passed both checks, now it is safe to update state
                current_version = incoming_version
                last_applied_seq = msg["cmd_seq"]
                print(f"[{node_id}] Received PLAY command, scheduled for: {msg['play_at']}")
                wait_time = msg["play_at"] - get_synced_time()
                if wait_time > 0:
                    time.sleep(wait_time)
                    print(f"[{node_id}] PLAYING NOW! Local time: {get_synced_time():.3f}")

            # 2. Handle STATE_SNAPSHOT (resync for nodes that missed the PLAY command)
            elif msg["type"] == "STATE_SNAPSHOT":
                incoming_version = msg.get("version", 1)
                # Compare local version with incoming snapshot version
                if incoming_version > current_version:
                    print(f"[{node_id}] CONFLICT: Local version {current_version} is stale! Adopting coordinator version {incoming_version}")
                    current_version = incoming_version
                    playback_state = "PLAYING"
                    wait_time = msg['play_at'] - get_synced_time()
                    if wait_time < 0:
                        elapsed = -wait_time
                        print(f"[{node_id}] RESUMED PLAYBACK! Snapped to {elapsed:.2f}s into track. Local time: {get_synced_time():.3f}")
                    else:
                        time.sleep(wait_time)
                        print(f"[{node_id}] PLAYING NOW AFTER RECOVERY! Local time: {get_synced_time():.3f}")
                else:
                    print(f"[{node_id}] REJECTED SNAPSHOT: Local version {current_version} >= incoming version {incoming_version}")

            # 3. Handle TIME_REPLY (Milestone 7: correct our clock, Cristian's algorithm)
            elif msg["type"] == "TIME_REPLY":
                t2 = get_synced_time()                    #our clock when the reply arrived
                round_trip = t2 - msg["t0"]               #how long the whole ask-and-answer took
                estimate = msg["coord_time"] + round_trip / 2  #guess: the reply took half the round trip
                correction = estimate - t2                #how far off our clock is
                clock_offset += correction                #shift the synced clock (raw clock untouched)
                print(f"[{node_id}] SYNC: round trip {round_trip*1000:.1f}ms, corrected clock by {correction*1000:+.1f}ms")
        except socket.timeout:
            pass
        except ConnectionResetError:
            # Windows "nobody home" note: the proxy/coordinator isn't listening right now.
            # Wait like a timeout would, so heartbeats keep their normal 0.5s pace.
            time.sleep(0.5)
except KeyboardInterrupt:
    print(f"\n[{node_id}] Stopped by user.")
finally:
    sock.close()
    print("Done.")