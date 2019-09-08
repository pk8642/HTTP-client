import re
import socket

#  TODO add headers and handle them

class Request:
    def __init__(self, uri, method='GET', body='', header='', to=15):
        self._method = method
        self._uri = uri
        self._body = body
        self._header = header
        self._timeout = to

        self._PORT = 80

    def send_data(self, sock):
        host, path = self._parse_uri()
        self._connect(host, sock)
        sock.sendall(self._form_message(path, host))

    def _connect(self, host, sock):
        try:
            sock.connect((host, self._PORT))
        except OSError:
            sock = socket.socket()
            sock.connect((host, self._PORT))


    def _parse_uri(self):
        path = '/'
        matches = re.findall('//', self._uri)
        if len(matches) > 1:
            raise ValueError('incorrect uri')
        elif len(matches) == 1:
            if re.match('http:', self._uri):
                self._uri = self._uri[7:]
            elif re.match('www\.', self._uri):
                pass
            else:
                raise ValueError('incorrect uri')

        host = self._uri.split('/')[0]
        if '/' in self._uri:
            path = self._uri[len(host):]
        return host, path

    def _form_message(self, path, host):
        message = f'{self._method} {path} HTTP/1.1\r\n' \
                  f'Host: {host}\r\n' \
                  f'{self._header}\r\n' \
                  f'\r\n' \
                  f'{self._body}'

        return bytes(message, encoding='utf8')

        # self.type = None
        # self.subtype = None
        # self.charset = None
        # self.media_type = self.type, self.subtype, self.charset
        # # i.e. 'text/html;charset=utf-8'
        # self.Content_Type = self.media_type
        #
        # self.content_coding = None  # i.e. 'gzip'
        # self.Content_Encoding = self.content_coding
        #
        # self.language_tag = None# i.e. 'fr, en-US, es-419, az-Arab'
        # self.Content_Language = self.language_tag
        # self.Content_Location = None # TODO
