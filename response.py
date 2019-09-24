import re
import gzip


# TODO add handling codes
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

            if not self.flag:  # if it's HEAD request, there's no body
                try:
                    content_length = self.headers['content-length']
                    self.static_recv(fd, int(content_length))
                except KeyError:
                    self.dynamic_recv(fd)

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

            try:
                connection = self.headers['connection']
                if re.match(r'close', connection):
                    self.connection = False
            except KeyError:
                pass

    def receive_headers(self, reader):
        self.headers['code'] = reader.readline().decode('utf8')
        print(self.headers['code'])
        header = reader.readline().decode('utf8')
        while header != '\r\n':
            self.response_headers += header
            key, value = header.split(': ')
            if key == 'Set-Cookie':
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
        self.response_body = reader.read(length)

    def dynamic_recv(self, reader):
        chunk_size = get_chunk_size(reader)
        while chunk_size != 0:
            self.response_body += reader.read(chunk_size)
            chunk_size = get_chunk_size(reader)
