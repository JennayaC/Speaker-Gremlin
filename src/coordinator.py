"""
Speaker Gremlins - Coordinator

- Listens for heartbeat messages from speaker nodes and coordinates their playback.
- Detects silent failures and timeouts triggered by chaos proxy or network issues.
- Monitors Clock Drift between the nodes and the coordinator.
- Sends a PLAY command to all nodes so that they can play in sync. 
- Manages duplicated messages and only sends the latest version of the command to the nodes.
- Sends information about its current state to reconnected node for resynchronization.

"""
import socket
import time
import json

#Socket setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(('127.0.0.1',5001))
sock.settimeout(1) #prevents program from hanging on recvfrom

print(f"Listening for heartbeats from nodes...")

#Variables to keep track of node states (detected, lost, etc.)
last_seen_sequence = {} #Dictionary to keep track of the last sequence number seen from each node
detected_nodes = {} #Dictionary to keep track of when each node was last heard from
node_ports = {} #Dictionary to keep track of the port number for each node
lost_nodes = set() #Set to keep track of nodes that have been lost


#Variables to keep track of cluster state
playback_state = "IDLE" #Current state of the cluster
play_sent = False #Boolean to keep track of whether the PLAY command has been sent
target_play_time = None #timestamp of when playback should start
command_sequence = 0 #Sequence number for commands to avoid duplicates 
state_version = 1 #Version number for state updates when node reconnects to cluster

#Main loop
try:
    while True:
        try:
            data, addr = sock.recvfrom(2048)
            recv_time = time.time()

            msg = json.loads(data.decode())

            node = msg['node']
            seq = msg['seq']

            detected_nodes[node] = recv_time
            if "port" in msg:
                node_ports[node] = msg["port"]
            expected_ts = recv_time

            # 1. Clock Error (Drift)
            local_ts = msg['sender_ts']
            error_msg = (local_ts - expected_ts) * 1000
            print(f"[{node}] Expected: {expected_ts:.3f} | Local: {local_ts:.3f} | Error: {error_msg:+.1f}ms")

            # 2. Packet Loss and Sequence Order Detection
            if node in last_seen_sequence:
                expected = last_seen_sequence[node] + 1
                if seq < last_seen_sequence[node]:
                    print(f"Node {node} sequence reset")
                elif seq > expected:
                    lost_packet_count = seq - expected
                    print(f"!!! {node} MISSED {lost_packet_count} packets!")
                    
            last_seen_sequence[node] = seq

            # 3. Node Recovery and State Synchronization
            if node in lost_nodes:
                print(f"Node {node} is back online!")
                lost_nodes.remove(node)
                if playback_state == "PLAYING":
                    snapshot = {
                        "type": "STATE_SNAPSHOT", 
                        "play_at": target_play_time,
                        "playback_state": playback_state,
                        "version": state_version
                    }
                    payload = json.dumps(snapshot).encode()
                    sock.sendto(payload, ('127.0.0.1', node_ports[node]))
                    print(f"Sent state snapshot to recovered node {node}")

            # 4. Sending Playback Command
            if play_sent == False and len(detected_nodes) == 3:
                target_play_time = time.time() + 2.0
                command_sequence += 1
                play_cmd = {
                    "type": "PLAY",
                    "sender_ts": time.time(),
                    "play_at": target_play_time,
                    "cmd_seq": command_sequence,
                    "version": state_version
                }
                payload = json.dumps(play_cmd).encode()
                print(f"Sent PLAY command to nodes, scheduled for: {target_play_time:.3f}")
                for port in node_ports.values():
                    sock.sendto(payload, ('127.0.0.1', port))
                    #sock.sendto(payload, ('127.0.0.1', port)) #Deliberately send duplicate command (Commented out for now, this was for testing)
                playback_state = "PLAYING"
                play_sent = True
        
        except socket.timeout:
            pass

        # Check for State Consistency / Lost Nodes
        for node_id in detected_nodes:
            time_since_last_heartbeat = time.time() - detected_nodes[node_id]
            if time_since_last_heartbeat > 2.5 and node_id not in lost_nodes:
                # If a node has been lost for more than 2.5 seconds, the coordinator assumes it missed the PLAY command
                state_version += 1
                target_play_time -= 5.0 #This tracks the amount of time elapsed since the node was lost
                print(f"***CLUSTER STATE CHANGED: Coordinator bumped state to version {state_version}***")
                print(f"Node {node_id} heartbeat lost")
                lost_nodes.add(node_id)
except KeyboardInterrupt:
    print("\nCoordinator stopped by user.")
finally:
    sock.close()
    print("Done.")

