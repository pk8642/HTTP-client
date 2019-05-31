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
        self.socket.settimeout(args['timeout'])

        self.message = self.form_message()
        self.charset = 'utf-8'
        self.type = 'text'
        self.ext = 'html'

    def upd_data(self, args, path=None):
        self.method = args['method']
        self.body = args['body']
        self.header = args['header']
        if path:
            self.path = path
        self.message = self.form_message()

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
        self.socket.sendall(bytes(self.message, encoding=self.charset))
        self.receive()

    def receive(self):
        headers = self.receive_headers()

        charset = re.findall(r'charset=\S*', headers)

        type = re.search(r'Content-Type: (?P<type>\w+)/(?P<ext>\w+)', headers)

        if type.group('type') == 'image':
            self.type = 'image'
            self.ext = type.group('ext')

        if charset:
            self.charset = charset[0].split('=')[1]
        content_length = re.search(r'Content-Length: (?P<size>\d+)', headers)

        if content_length:
            self.static_recv(int(content_length.group('size')))
        else:
            self.dynamic_recv()

    def receive_headers(self):
        result = self.socket.recv(128).decode(self.charset)
        while '\r\n\r\n' not in result:
            result += self.socket.recv(1).decode(self.charset)
        print(result)
        return result

    def static_recv(self, length):
        f = open(f'received.{self.ext}', 'wb')
        while length > 4000:
            packet = self.socket.recv(3500)
            print(packet)
            f.write(packet)
            f.flush()
            length -= len(packet)

        packet = self.socket.recv(length)
        f.write(packet)
        # print(packet)
        f.flush()
        print('file is ready to be seen')
        f.close()

    def dynamic_recv(self):
        chunk_size = self.get_chunk_size()
        f = open(f'received.{self.ext}', 'wb')
        while chunk_size != 0:
            data = self.socket.recv(chunk_size)
            size = len(data)

            while size < chunk_size:
                data += self.socket.recv(chunk_size-size)
                size += len(data)
            f.write(data)
            # print(data)
            f.flush()
            chunk_size = self.get_chunk_size()
        print('file is ready to be seen')
        f.close()

    def get_chunk_size(self):
        hex_chunk_size = self.socket.recv(4).decode('utf-8')
        time.sleep(0.1)

        while len(re.findall(r'[\da-fA-F]+\r\n', hex_chunk_size)) == 0:
            hex_chunk_size += self.socket.recv(1).decode('utf-8')
            time.sleep(0.01)

        return int(hex_chunk_size, 16)
