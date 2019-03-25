import socket


class Request:
    def __init__(self, namespace):
        self.host = namespace[0]
        self.path = namespace[1]
        self.method = namespace[2]
        self.body = namespace[3]
        self.header = namespace[4]

    def send_request(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, 80))
            message = '{0} /{1} HTTP/1.1\r\nHost: {2}\r\n\r\n'.format(
                self.method, self.path, self.host
            )
            sock.sendall(bytes(message, encoding='utf-8'))
            return sock.recv(1000)
