import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(('127.0.0.1', 5001))

print("Waiting for message from coordinator...")

data, addr = sock.recvfrom(1024)
print(f"Recieved: {data.decode()} from {addr}")








