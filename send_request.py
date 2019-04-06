import socket
import re
import time


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
        answer = re.search(r'HTTP/\d\.\d (?P<code>\d{3})', headers)

        if answer.group('code')[0] != '2':
            raise ConnectionError(answer.group('code'))

        self.charset = re.findall(r'charset=\S*', headers)[0].split('=')[1]
        content_length = re.search(r'Content-Length: (?P<size>\d+)', headers)

        if content_length:
            self.static_recv(int(content_length.group('size')))
        else:
            self.dynamic_recv()

    def receive_headers(self):
        result = self.socket.recv(128).decode(self.charset)
        while '\r\n\r\n' not in result:
            result += self.socket.recv(1).decode(self.charset)

        index = result.find('\r\n\r\n')
        message_part = result[index + 4:]
        return result, message_part

    def static_recv(self, length):
        f = open('received.html', 'w', encoding=self.charset)

        packet = self.socket.recv(length).decode(self.charset)

        f.write(packet)
        f.flush()
        f.close()

    def dynamic_recv(self):
        chunk_size = self.get_chunk_size()
        f = open('received.html', 'w', encoding=self.charset)
        while chunk_size != 0:
            data = self.socket.recv(chunk_size).decode(self.charset)
            size = len(data)

            while size < chunk_size:
                data += self.socket.recv(chunk_size-size).decode(self.charset)
                size += len(data)
            f.write(data)
            f.flush()
            chunk_size = self.get_chunk_size()
        f.close()

    def get_chunk_size(self):
        hex_chunk_size = self.socket.recv(4).decode()
        time.sleep(0.1)

        while len(re.findall(r'[\da-fA-F]+\r\n', hex_chunk_size)) == 0:
            hex_chunk_size += self.socket.recv(1).decode()
            time.sleep(0.01)

        return int(hex_chunk_size, 16)
