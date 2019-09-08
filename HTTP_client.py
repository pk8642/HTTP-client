import socket
import parse_line
from request import Request
from response import Response

import re

#  TODO cookies
if __name__ == '__main__':
    try:
        while True:
            with socket.socket() as sock:
                line = input('>').split()
                if re.match(r'cls|close', line[0]):
                    raise KeyboardInterrupt
                #elif re.findall(r'-\w+', line[1]):
                else:
                    namespace = parse_line.create_parser().parse_args(line)
                    args = parse_line.convert_to_list(namespace)
                    request = Request(*args)
                # else:
                #     if len(line) > 1:
                #         print('ignored:', ' '.join(line[1:]))
                #     request = Request(line[0])
                request.send_data(sock)
                print(sock)
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
        print('client closed')
