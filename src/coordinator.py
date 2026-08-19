import socket
import time
import json
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

NODE_ADDR = ('127.0.0.1', 5001)
seq = 0

print("Coordinator started. Sending 5 SYNC messages...")

for _ in range(5):
    msg = {
        "type": "SYNC",
        "seq": seq,
        "sender_ts": time.time()
    }
    payload = json.dumps(msg).encode()
    sock.sendto(payload, NODE_ADDR)
    print(f"Sent: seq={msg['seq']}  type={msg['type']}  sender_ts={msg['sender_ts']:.4f}")

    seq += 1
    time.sleep(0.5)

sock.close()
print("Done.")

