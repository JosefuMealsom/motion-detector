import socket

class UdpSocket:
    def __init__(self, host, port):
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.server = (host, port)

    def send_message(self, message):
        self.socket.sendto(message.encode("utf-8"), self.server)
