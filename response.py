import re
import gzip
from tqdm import tqdm


def get_chunk_size(reader):
    hex_chunk_size = reader.readline().decode('utf8')
    if hex_chunk_size == '\r\n':
        hex_chunk_size += reader.readline().decode('utf8')

    return int(hex_chunk_size, 16)


class Response:
    def __init__(self, sock, HEAD_flag):
        self.sock = sock
        self.response_headers = ''
        self.response_body = b''

        self.flag = HEAD_flag

        self.headers = {}  # i.e. 'Content-Type: text/html'
        self.cookies = []  # cookie pairs

        self.filename = None
        self.ext = 'html'  # if url endswith '.some_ext' it will replace this
        self.charset = None
        self.connection = True

    def receive(self):
        with self.sock.makefile(mode='rb') as fd:
            self.receive_headers(fd)

            try:
                connection = self.headers['connection']
                if re.match(r'close', connection):
                    self.connection = False
            except KeyError:
                pass

            if not self.flag:  # if it's HEAD request, there's no body
                try:
                    content_length = self.headers['content-length']
                    self.static_recv(fd, int(content_length))
                except KeyError:
                    try:
                        _ = self.headers['transfer-encoding']
                        self.dynamic_recv(fd)
                    except KeyError:
                        return
                print(f"\r\n{self.headers['code']}")
                print(self.response_headers)

                try:
                    encoding = self.headers['accept-encoding']
                    if 'gzip' in encoding:
                        self.response_body = gzip.decompress(
                            self.response_body)
                except KeyError:
                    pass

                try:
                    cont_type = self.headers['content-type']
                    if re.search(r'charset', cont_type) is not None:
                        self.charset = cont_type.split('=')[1]
                except KeyError:
                    pass

    def receive_headers(self, reader):
        self.headers['code'] = reader.readline().decode('utf8')
        header = reader.readline().decode('utf8')
        while header != '\r\n':
            self.response_headers += header
            key, value = header.split(': ', 2)
            if key == 'Set-Cookie':
                if not 'deleted' in value:
                    self.cookies.append(value)
            else:
                self.headers[key.casefold()] = value
            header = reader.readline().decode('utf8')

    def save_to_file(self, path):
        self.get_filename(path)
        with open(f'{self.filename}.{self.ext}', 'wb') as f:
            f.write(self.response_body)
            f.flush()
        print('file is ready to be seen')

    def get_filename(self, path):
        try:
            ext_dot_index = path.rindex('.')
        except ValueError:
            ext_dot_index = 0
        if ext_dot_index > path.rindex('/'):
            file = path.rsplit('/', 1)[1]
            self.filename, self.ext = file.rsplit('.', 1)
            return

        if not self.filename:
            try:
                self.filename = re.search(
                    rb'<title>.*</title>',
                    self.response_body
                )[0][7:-8].decode(self.charset)
            except ValueError:
                self.filename = 'received'

    def print(self):
        print(self.response_headers)
        if self.charset is not None:
            print(self.response_body.decode(self.charset))
        else:
            print(self.response_body)

    def static_recv(self, reader, length):
        pbar = tqdm(total=length)
        for i in range(length):
            self.response_body = reader.read(1)
            pbar.update(1)
        pbar.close()

    def dynamic_recv(self, reader):
        chunk_size = get_chunk_size(reader)
        while chunk_size != 0:
            self.static_recv(reader, chunk_size)
            chunk_size = get_chunk_size(reader)
