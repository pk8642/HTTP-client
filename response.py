import re
import gzip
from tqdm import tqdm


def get_chunk_size(reader):
    hex_chunk_size = reader.readline().decode('utf8')
    if hex_chunk_size == '\r\n':
        hex_chunk_size += reader.readline().decode('utf8')

    return int(hex_chunk_size, 16)


class Response:
    def __init__(self, sock):
        self.sock = sock
        self.response_headers = ''
        self.response_body = b''

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

            try:
                content_length = self.headers['content-length']
                self.static_recv(fd, int(content_length))
            except KeyError:
                try:
                    _ = self.headers['transfer-encoding']
                    self.dynamic_recv(fd)
                except KeyError:
                    return
            self.print_headers()

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
            values = header.split(': ')
            key = values[0]
            value = ':'.join(values[1:])
            if key == 'Set-Cookie':
                if 'deleted' not in value:
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
                filename = re.search(
                    rb'<title>.*</title>',
                    self.response_body
                )
                if filename is None:
                    raise ValueError

                self.filename = filename[0][7:-8].decode(self.charset)
            except ValueError:
                self.filename = 'received'

    def print(self):
        if self.charset is not None:
            print(self.response_body.decode(self.charset))
        else:
            print(self.response_body)

    def print_headers(self):
        print(f"\r\n{self.headers['code']}")
        print(self.response_headers)

    def static_recv(self, reader, length, pbar=None):
        if not pbar:
            pbar = tqdm(total=length)
        count_of_updates = 11
        fragment = length // count_of_updates
        remain = length % count_of_updates
        for i in range(count_of_updates):
            self.response_body += reader.read(fragment)
            pbar.update(fragment)
        self.response_body += reader.read(remain)
        pbar.update(remain)
        if pbar.total == length:
            pbar.close()

    def dynamic_recv(self, reader):
        pbar = tqdm(total=65536)
        chunk_size = get_chunk_size(reader)
        while chunk_size != 0:
            if len(self.response_body) + chunk_size > pbar.total:
                raising_total = (len(self.response_body) + chunk_size) * 2
                pbar.total += raising_total
            self.static_recv(reader, chunk_size, pbar)
            chunk_size = get_chunk_size(reader)

        pbar.total = len(self.response_body)
        pbar.close()
