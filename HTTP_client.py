import socket
import parse_line
from request import Request
from response import Response
import pickle
import re

sockets = {}  # host: socket
cookies = {}  # host: [cookie-headers]

COOKIES = 'cookies'  # file where cookies are saved


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
        try:
            with open(COOKIES, 'rb') as f:
                cookies = pickle.load(f)
        except FileNotFoundError:
            pass
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
                request.set_cookies(cookies)
            try:
                sock = request.send_data(sockets)
            except socket.gaierror:
                print('I don\'t know this address :(')
                continue

            if args[0] == 'HEAD':
                flag = True
            else:
                flag = False
            response = Response(sock, flag)

            response.receive()
            if not response.connection:
                sockets[host].close()
                del sockets[host]
                print('closed connection with:', host)
            if response.cookies:
                cookies[host] = []
                for cookie in response.cookies:
                    if not 'deleted' in cookie:
                        cookies[host].append(cookie)

            ask_about_print = input(
                'Would you like to print response?(y/n): '
            )
            if re.match(r'[Yy]', ask_about_print):
                response.print()
            ask_about_file = input(
                'Would you like to save response to a file?(y/n): '
            )
            if re.match(r'[Yy]', ask_about_file):
                response.save_to_file(path)
    except KeyboardInterrupt:
        print('closing connections')
        for host in sockets:
            sockets[host].close()
            print('closed connection with:', host)
        print('all done')
        print('client closed')

    if len(cookies) > 0:
        with open(COOKIES, 'wb') as f:
            pickle.dump(cookies, f)
