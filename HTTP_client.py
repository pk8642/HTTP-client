import socket
import parse_line
from request import Request
from response import Response

import re

sockets = {} #  serving opened sockets with host as key
#  TODO cookies
if __name__ == '__main__':
    try:
        while True:
            line = input('>').split()
            if re.match(r'cls|close', line[0]):
                raise KeyboardInterrupt
            else:
                namespace = parse_line.create_parser().parse_args(line)
                args = parse_line.convert_to_list(namespace)
                request = Request(*args)
            try:
                sock = request.send_data(sockets)
            except socket.gaierror:
                print('I don\'t know this address :(')
                continue

            response = Response(sock)
            response.receive()

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
            sockets[host].close()
            print('closed connection with:', host)
        print('all done')
        print('client closed')
