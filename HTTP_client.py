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
    _path = '/'

    if re.match('http://', uri):
        uri = uri[7:]
    elif re.match(r'https://', uri):
        print('I can\'t work with https :(')
        raise ValueError()

    _host = uri.split('/')[0]
    if '/' in uri:
        _path += uri[len(_host) + 1:]
    return _host, _path


def send(_lines):
    namespace = parse_line.create_parser().parse_args(_lines)
    args = parse_line.convert_to_list(namespace)
    _host, _path = parse_uri(args[0])
    del args[0]
    _request = Request(_host, _path, *args)
    _request.set_cookies(cookies)
    try:
        _sock = _request.send_data(sockets)
    except socket.gaierror:
        print('I don\'t know this address :(')
        raise socket.gaierror
    return _sock, _host, _path


def get(_sock, _host, _line):
    _response = Response(_sock)
    if re.search(r'HEAD', _line):
        _response.receive_headers(_sock.makefile(mode='rb'))
        _response.print_headers()
    else:
        _response.receive()

    if not _response.connection:
        _response.print()
        sockets[_host].close()
        del sockets[_host]
        print('closed connection with:', _host)
    return _response


def main():
    try:
        try:
            with open(COOKIES, 'rb') as f:
                global cookies
                cookies = pickle.load(f)
        except FileNotFoundError:
            pass
        while True:
            line = input('\r\n>').split()
            if re.match(r'cls|close', line[0]):
                raise KeyboardInterrupt
            else:
                try:
                    sock, host, path = send(line)
                except socket.gaierror:
                    continue

            response = get(sock, host, ' '.join(line))

            while re.search(r'3\d\d', response.headers['code']):
                try:
                    addr = response.headers['location'][:-2]
                    confirm = input(f'Confirm to go to this addr: '
                                    f'{addr}: ')
                    if confirm == 'y':
                        sockets[host].close()
                        del sockets[host]
                        try:
                            line[0] = addr
                            sock, host, path = send(line)
                        except ValueError:
                            continue
                        response = get(sock, host, ' '.join(line))
                    else:
                        continue
                except KeyError:
                    print('there\'s no address to go')

            cookies[host] = response.cookies

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


if __name__ == '__main__':
    main()
