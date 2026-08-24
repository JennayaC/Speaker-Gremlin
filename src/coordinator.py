import socket
import time
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(('127.0.0.1',5001))

print(f"Listening for heartbeats from nodes...")
detected_nodes = {}
sock.settimeout(2)

while True:
    try:
        data, addr = sock.recvfrom(2048)
        recv_time = time.time()

        msg = json.loads(data.decode())
        detected_nodes[msg["node"]] = recv_time
        print(detected_nodes)
    
    except socket.timeout:
        pass

    for node_id in detected_nodes:
        time_since_last_heartbeat = time.time() - detected_nodes[node_id]
        if time_since_last_heartbeat > 2.5:
            print(f"Node {node_id} heartbeat lost")
        
        





    
   

sock.close()
print("Done.")

