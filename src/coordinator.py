import socket
import time
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(('127.0.0.1',5001))

print(f"Listening for heartbeats from nodes...")

last_seen_sequence = {}
detected_nodes = {}
lost_nodes = set()
sock.settimeout(1)

while True:
    try:
        data, addr = sock.recvfrom(2048)
        recv_time = time.time()

        msg = json.loads(data.decode())

        node = msg['node']
        seq = msg['seq']

        if node in last_seen_sequence:
            expected = last_seen_sequence[node] + 1
            if seq != expected:
                lost_packet_count = seq - expected
                print(f"!!! {node} MISSED {lost_packet_count} packets!")
                
        last_seen_sequence[node] = seq
    
        if msg["node"] in lost_nodes:
            print(f"Node {msg['node']} is back online!")
            lost_nodes.remove(msg["node"])

        detected_nodes[msg["node"]] = recv_time
        print(detected_nodes)
    
    except socket.timeout:
        pass

    for node_id in detected_nodes:
        time_since_last_heartbeat = time.time() - detected_nodes[node_id]
        if time_since_last_heartbeat > 2.5 and node_id not in lost_nodes:
            print(f"Node {node_id} heartbeat lost")
            lost_nodes.add(node_id)
        
        





    
   

sock.close()
print("Done.")

