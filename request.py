import re
import socket

#  TODO add headers and handle them

class Request:
    def __init__(self, uri, method, body, headers, to=15):
        self._method = method
        self._uri = uri
        self._body = body
        self._headers = headers
        self._timeout = to

        self._PORT = 80

    def send_data(self, sockets):
        host, path = self._parse_uri()
        try:
            sock = sockets[host]
        except KeyError:
            sock = socket.socket()
            sock.connect((host, self._PORT))
            sockets[host] = sock
        sock.sendall(self._form_message(path, host))
        return sock

    @property
    def _method(self):
        return self.__method

    @_method.setter
    def _method(self, method):
        if re.match(r'GET|PUT|POST|HEAD|OPTIONS|DELETE', method) is None:
            raise ValueError('incorrect method')
        else:
            self.__method = method

    def _parse_uri(self):
        path = '/'
        matches = re.findall('//', self._uri)
        if len(matches) > 1:
            raise ValueError('incorrect uri')
        elif len(matches) == 1:
            if re.match('http:', self._uri):
                self._uri = self._uri[7:]
            elif re.match('www\.', self._uri):
                self._uri = self._uri[4:]
            else:
                raise ValueError('incorrect uri')

        host = self._uri.split('/')[0]
        if '/' in self._uri:
            path = self._uri[len(host):]
        return host, path

    def _form_message(self, path, host):
        message = f'{self._method} {path} HTTP/1.1\r\n' \
                  f'Host: {host}\r\n' \
                  f'{self._headers}\r\n' \
                  f'\r\n' \
                  f'{self._body}'
        return bytes(message, encoding='utf8')
