import re
import socket
import gzip
from datetime import datetime


class Request:
    def __init__(self, host, path, method, body, headers, to=15):
        self._method = method
        self._host = host
        self._path = path
        self._body = body
        self._headers = headers
        self._timeout = to

        self._PORT = 80

    @property
    def _method(self):
        return self.__method

    @_method.setter
    def _method(self, method):
        if re.match(r'GET|PUT|POST|HEAD|OPTIONS|DELETE', method) is None:
            raise ValueError('incorrect method')
        else:
            self.__method = method

    def send_data(self, sockets):
        try:
            sock = sockets[self._host]
        except KeyError:
            sock = socket.socket()
            sock.connect((self._host, self._PORT))
            sockets[self._host] = sock
        sock.settimeout(self._timeout)
        self._modify_data()

        msg = self._form_message(self._path, self._host)
        print(msg)
        sock.sendall(msg + self._body)
        return sock

    def set_cookies(self, cookies):
        header = []
        for cookie in cookies:
            pairs = cookie.split('; ')
            for i in range(len(pairs), 0, -1):
                pair = pairs[i]
                if re.match(r'[Pp]ath', pair):
                    if not self._host.startswith(pair.split('=')[0]):
                        break
                elif re.match(r'[Ee]xpired', pair):
                    expires_at = datetime.strptime(pair.split('=')[0],
                                                   '%a, %d-%b-%Y %H:%M:%S %Z')
                    # Thu, 01-Jan-1970 00:00:01 GMT
                    if datetime.utcnow() > expires_at:
                        break
                header.append(pairs[0])
        if header:
            self._headers.append(f'Cookie: {"; ".join(header)}')

    def _modify_data(self):
        charset = 'utf8'
        compression = None

        if not self._body.endswith('\r\n\r\n') and len(self._body) > 0:
            self._body += '\r\n\r\n'

        for header in self._headers:
            if header.casefold() == 'content-type':
                charset = header.split('=')[1]
            elif header.casefold() == 'accept-encoding':
                compression = header.split(': ')

        self._body = self._body.encode(charset)

        if compression is not None:
            if compression == 'gzip':
                gzip.compress(self._body)

        if self._body:
            self._headers.append(f'Content-Length: {len(self._body - 4)}\r\n')

    def _form_message(self, path, host):
        self._headers = '\r\n'.join(self._headers)
        message = f'{self._method} {path} HTTP/1.1\r\n' \
                  f'Host: {host}\r\n' \
                  f'{self._headers}\r\n'
        return bytes(message, encoding='utf8')
