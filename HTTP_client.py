import socket
import parse_line
from request import Request
from response import Response

import re

sockets = {}  # host: (socket, [cookies])


#  serving opened sockets and their cookies with host as key

def parse_uri(uri):
    path = '/'

    if re.match('http://', uri):
        uri = uri[7:]
    elif re.match(r'https://', uri):
        raise ValueError('I can\'t work with https :(')

    host = uri.split('/')[0]
    if '/' in uri:
        path += uri[len(host):]
    return host, path


if __name__ == '__main__':
    try:
        while True:
            line = input('>').split()
            if re.match(r'cls|close', line[0]):
                raise KeyboardInterrupt
            else:
                namespace = parse_line.create_parser().parse_args(line)
                args = parse_line.convert_to_list(namespace)
                host, path = parse_uri(args[0])
                del args[0]
                print(args)
                request = Request(host, path, *args)
                try:
                    request.set_cookies(sockets[host][1])
                except KeyError:
                    pass
            try:
                sock = request.send_data(sockets)
            except socket.gaierror:
                print('I don\'t know this address :(')
                continue

            response = Response(sock)

            try:
                ext_dot_index = path.rindex('.')
            except ValueError:
                ext_dot_index = 0
            if ext_dot_index > path.rindex('/'):
                file = path.rsplit('/', 1)[1]
                response.filename, response.ext = file.rsplit('.', 1)
            response.receive()
            if not response.connection:
                sockets[host][0].close()
                del sockets[host]
                print('closed connection with:', host)
            else:
                cookies = response.set_cookies()
                sockets[host][1].clear()
                sockets[host][1].extend(cookies)

            ask_about_print = input(
                'Would you like to print response?(y/n): '
            )
            if re.match(r'[Yy]', ask_about_print):
                response.print()
            ask_about_file = input(
                'Would you like to save response to a file?(y/n): '
            )
            if re.match(r'[Yy]', ask_about_file):
                response.save_to_file()
    except KeyboardInterrupt:
        print('closing connections')
        for host in sockets:
            sockets[host][0].close()
            print('closed connection with:', host)
        print('all done')
        print('client closed')
