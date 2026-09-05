import socket
import random
import time
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 5002))

while True:
    data, addr = sock.recvfrom(2048)
    drop = random.random()
    if drop < 0: #temporary changing dropiut rate to 0 for latency testing
        print(f"Drop heartbeat from {addr}")
        continue
    else:
        #random delay in range between 0 and 0.3
        random_delay = random.random() * 0.3
        time.sleep(random_delay) 
        sock.sendto(data,('127.0.0.1',5001))
        print(f"Forward heartbeat from {addr}")
        print(f"Delay: {random_delay * 1000:.1f}ms")

        
        

