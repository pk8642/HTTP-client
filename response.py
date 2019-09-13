import re
import time
#  TODO add headers and handle them

def receive_headers(reader):
    result = ''
    while result[-4:] != '\r\n\r\n':
        result += reader.readline().decode('utf8')
    print(result)
    return result


def get_chunk_size(reader):
    hex_chunk_size = reader.readline().decode('utf8')
    if hex_chunk_size == '\r\n':
        hex_chunk_size += reader.readline().decode('utf8')

    return int(hex_chunk_size, 16)


class Response:
    def __init__(self, sock):
        self.sock = sock
        self.response = b''

        self.headers = {}  # header: value

        self.charset = None
        self.type = None
        self.ext = None

    def receive(self):
        with self.sock.makefile(mode='rb') as fd:

            headers = receive_headers(fd)

            charset = re.findall(r'[Cc]harset=\S*', headers)

            type = re.search(r'Content-Type: (?P<type>\w+)/(?P<ext>\w+)', headers)

            if type:
                self.type = type.group('type')
                self.ext = type.group('ext')

            content_length = re.search(r'Content-Length: (?P<size>\d+)', headers)

            if content_length:
                self.static_recv(fd, int(content_length.group('size')))
            else:
                self.dynamic_recv(fd)

            if charset:
                self.charset = charset[0].split('=')[1]
                self.response.decode(self.charset)

    def _parse_headers(self, headers):
        pass

    def save_to_file(self):
        with open(f'received.{self.ext}', 'wb') as f:
            f.write(self.response)
            f.flush()
        print('file is ready to be seen')

    def print(self):
        print(self.response)

    def static_recv(self, reader, length):
        self.response = reader.read(length)

    def dynamic_recv(self, reader):
        chunk_size = get_chunk_size(reader)
        while chunk_size != 0:
            self.response += reader.read(chunk_size)
            chunk_size = get_chunk_size(reader)

