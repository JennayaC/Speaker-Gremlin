import socket
import time
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(('127.0.0.1', 5001))

print("Speaker node listening on port 5001...\n")

for _ in range(5):
    data, addr = sock.recvfrom(1024)
    recv_ts = time.time()

    msg = json.loads(data.decode())
    delta_ms = (recv_ts - msg['sender_ts']) * 1000

    print(f"Recieved: seq={msg['seq']}  type={msg['type']}  sender_ts={msg['sender_ts']:.4f}")
    print(f"Received at: {recv_ts:.4f}")
    print(f"Delta: {delta_ms:.2f} ms")

sock.close()
print("\nDone.")








