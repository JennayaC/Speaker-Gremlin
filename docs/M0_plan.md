Goal:
Create a UDP 'connection' between two python processes. The sender sends a UDP packet to the reciever. Optionally the reciever can send a reply to comfirm it got the message. 

Main Concept:
Understanding the purpose of IP addresses, sockets, and port numbers. Also understanding separate processes and how they communicate through a socket across a network.

Moving parts: 
There should be a functional sender and reciever relationship. However this is UDP so there is no handshake necessary. 
coordinator.py --> sender
speaker_node.py --> reciever

Sequence:
1. Sender sends a UDP packet.
2. Receiver receives the packet.
3. Receiver prints what it received.
4. Receiver sends a reply to sender.
5. Sender prints the reply.

Solution: 
When both scripts are running, the corrdinator prints 'Message sent' and the speaker_node prints 'Message received'. If the terminal shows this message then M0 is done.
