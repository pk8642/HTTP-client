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
        try:
            cookies[self._host]
        except KeyError:
            return

        header = []
        time_parse = ['%a, %d %b %Y %H:%M:%S %Z', '%a, %d-%b-%Y %H:%M:%S %Z',
                      '&a %b %d %H:%M:%S %Y']

        for cookie in cookies[self._host]:
            pairs = cookie[:-2].split('; ')
            for i in range(len(pairs) - 1, -1, -1):
                pair = pairs[i]
                if i == 0:
                    header.append(pairs[i])

                if re.match(r'[Pp]ath', pair):
                    if not self._path.startswith(pair.split('=')[1]):
                        break
                elif re.match(r'[Ee]xpires', pair):
                    expires_at = None
                    for time in time_parse:
                        try:
                            expires_at = datetime.strptime(pair.split('=')[1],
                                                           time)
                            break
                        except ValueError:
                            continue
                    if not expires_at:
                        print('I\'ve got bad time')

                    if datetime.utcnow() > expires_at:
                        break
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
            self._headers.append(f'Content-Length: {len(self._body) - 4}\r\n')
        elif len(self._headers) > 0:
            self._headers[-1] += '\r\n'

    def _form_message(self, path, host):
        self._headers = '\r\n'.join(self._headers)
        message = f'{self._method} {path} HTTP/1.1\r\n' \
                  f'Host: {host}\r\n' \
                  f'{self._headers}\r\n'
        return bytes(message, encoding='utf8')
