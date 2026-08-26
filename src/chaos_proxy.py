import socket
import random

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 5002))

while True:
    data, addr = sock.recvfrom(2048)
    drop = random.random()
    if drop < 0.20:
        print(f"Drop heartbeat from {addr}")
        continue
    else:
        sock.sendto(data,('127.0.0.1',5001))
        print(f"Forward heartbeat from {addr}")
        
        

