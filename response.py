import re
import time
#  TODO add headers and handle them

class Response:
    def __init__(self, sock):
        self.sock = sock
        self.response = b''

        self.Code = None
        self.Accept = None
        self.Accept_Charset = None
        self.Accept_Encoding = None
        self.Accept_Language = None
        self.Cache_Control = None
        self.Connection = None
        self.Content_Encoding = None
        self.Content_Language = None
        self.Content_Length = None
        self.Content_Type = None
        self.Transfer_Encoding = None

        self.charset = 'utf-8'
        self.type = 'text'
        self.ext = 'html'

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
        result = self.sock.recv(128).decode(self.charset)
        while '\r\n\r\n' not in result:
            result += self.sock.recv(1).decode(self.charset)
        return result

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
            data = self.sock.recv(chunk_size)
            size = len(data)

            while size < chunk_size:  # если не все данные получит
                data += self.sock.recv(chunk_size - size)
                size += len(data)
            self.response += data
            chunk_size = self.get_chunk_size()

    def get_chunk_size(self):
        hex_chunk_size = self.sock.recv(4).decode('utf-8')
        time.sleep(0.1)

        while len(re.findall(r'[\da-fA-F]+\r\n', hex_chunk_size)) == 0:
            hex_chunk_size += self.sock.recv(1).decode('utf-8')
            time.sleep(0.01)

        return int(hex_chunk_size, 16)

