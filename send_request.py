import socket
import re


class Request:
    def __init__(self, args):
        self.host, self.path = args['uri']
        self.method = args['method']
        self.body = args['body']
        self.header = args['header']

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message = self.form_message()
        self.charset = 'utf-8'

    def form_message(self):
        message = '{0} {1} HTTP/1.1\r\nHost: {2}\r\n{3}\r\n\r\n{4}'.format(
            self.method,
            self.path,
            self.host,
            self.header,
            self.body
        )
        return message

    def send(self):
        self.socket.connect((self.host, 80))
        self.socket.sendall(bytes(self.message, encoding=self.charset))
        try:
            self.receive()
        finally:
            self.socket.close()

    def receive(self):
        headers, message = self.receive_headers()
        self.charset = re.findall(r'charset=\S*', headers)[0].split('=')[1]
        if 'Content-Length' in headers:
            self.static_recv(
                int(re.findall(r'Content-Length: \d+', headers)[0].split()[1]),
                message
            )
        elif 'Transfer-Encoding' in headers:
            self.dynamic_recv(message)

    def receive_headers(self):
        result = self.socket.recv(128).decode(self.charset)
        while '\r\n\r\n' not in result:
            result += self.socket.recv(1).decode(self.charset)
        index = result.find('\r\n\r\n')
        message_part = result[index + 4:]
        return result, message_part

    def static_recv(self, length, message):
        result = message
        result += self.socket.recv(length - len(message)).decode(self.charset)
        print(result)

    def dynamic_recv(self, message):
        result = message
        length = 0

        chunk_size = self.get_chunk_size()
        f = open('received.html', 'w', encoding=self.charset)
        while chunk_size > 0:
            data = self.socket.recv(chunk_size).decode(self.charset)
            self.socket.recv(2).decode(self.charset)
            result += data
            f.write(result)
            f.flush()
            length += chunk_size
            chunk_size = self.get_chunk_size()
        f.close()

    def get_chunk_size(self):
        hex_chunk_size = self.socket.recv(1).decode(self.charset)
        while len(re.findall(r'[\da-fA-F]+\r\n', hex_chunk_size)) == 0:
            hex_chunk_size += self.socket.recv(1).decode(self.charset)
        return int(hex_chunk_size, 16)
