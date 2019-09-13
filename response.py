import re
import time
#  TODO add headers and handle them

class Response:
    def __init__(self, sock):
        self.sock = sock
        self.response = b''

        self.headers = {}  # header: value

        self.charset = None
        self.type = None
        self.ext = None

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
        result = self.sock.recv(128).decode('utf8')
        while '\r\n\r\n' not in result:
            result += self.sock.recv(1).decode('utf8')
        print(result)
        return result

    def _parse_headers(self, headers):
        pass

    def save_to_file(self):
        with open(f'received.{self.ext}', 'wb') as f:
            f.write(self.response)
            f.flush()
        print('file is ready to be seen')

    def print(self):
        print(self.response)

    def static_recv(self, length):
        while length > 4000:
            packet = self.sock.recv(3500)
            self.response += packet
            length -= len(packet)

        packet = self.sock.recv(length)
        self.response += packet

    def dynamic_recv(self):
        chunk_size = self.get_chunk_size()
        while chunk_size != 0:
            self.static_recv(chunk_size)
            chunk_size = self.get_chunk_size()

    def get_chunk_size(self):
        hex_chunk_size = self.sock.recv(4).decode('utf-8')
        # time.sleep(0.1)

        while len(re.findall(r'[\da-fA-F]+\r\n', hex_chunk_size)) == 0:
            hex_chunk_size += self.sock.recv(1).decode('utf-8')
            time.sleep(0.01)

        return int(hex_chunk_size, 16)

