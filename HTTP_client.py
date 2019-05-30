import socket
import parse_line
import send_request

if __name__ == '__main__':
    parser = parse_line.create_parser()
    args = parse_line.convert_to_dict(parser.parse_args())
    if args['close']:
        print('The socket hasn\'t been opened yet')
        exit(1)
    request = send_request.Request(args)
    request.socket.connect((request.host, 80))
    request.send()
    while True:
        try:
            args = parse_line.convert_to_dict(parser.parse_args(input().split()))
            if args['close']:
                raise KeyboardInterrupt
            if args['uri'][0] == request.host:
                if args['uri'][1] == request.path:
                    request.upd_data(args)
                else:
                    request.upd_data(args, args['uri'][1])
            else:
                request = send_request.Request(args)
                request.socket.connect((request.host, 80))
            request.send()
        except KeyboardInterrupt:
            print('closing socket')
            break
    request.socket.shutdown(socket.SHUT_RDWR)
    request.socket.close()
    print('socket closed')
