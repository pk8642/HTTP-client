import socket


class Request:
    def __init__(self, parser):
        self.host = parser.host
        self.path = parser.path
        self.method = parser.method
        self.body = parser.body
        self.header = parser.header

    def send_request(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, 80))
            message = '{0} /{1} HTTP/1.1\r\nHost: {2}\r\n\r\n'.format(
                self.method, self.path, self.host
            )
            sock.sendall(bytes(message, encoding='utf-8'))
            return sock.recv(1000)
