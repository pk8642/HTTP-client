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
        self.charset = 'cp1251'

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
        if 'Content-Length' in headers:
            self.static_receive(
                int(re.findall(r'Content-Length: \d+', headers)[0].split()[1]),
                message
            )
        elif 'Transfer-Encoding' in headers:
            self.dynamic_receive(message)

    def receive_headers(self):
        result = self.socket.recv(1).decode(self.charset)
        while '\r\n\r\n' not in result:
            result += self.socket.recv(1).decode(self.charset)
        index = result.find('\r\n\r\n')
        message_part = result[index + 4:]
        return result, message_part

    def static_receive(self, length, message):
        result = message
        result += self.socket.recv(length - len(message)).decode(self.charset)
        print(result)

    def dynamic_receive(self, message):
        def get_chunk():
            chunk_length = int(re.search(r'[\da-fA-F]+', message)[0], 16)
            self.static_receive(chunk_length, message.split('\r\n')[1])

        while True:
            message = self.socket.recv(3).decode(self.charset)
            if '0\r\n\r\n' in message:
                break
            while '\r\n' not in message:
                message += self.socket.recv(1).decode(self.charset)
            get_chunk()
