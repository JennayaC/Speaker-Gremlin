import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = "Hello from coordinator!"

sock.sendto(message.encode(), ('127.0.0.1', 5001))

print("Message sent")
