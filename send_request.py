import socket


def send(request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((request.host, 80))
        message = '{0} {1} HTTP/1.1\r\nHost: {2}\r\n{3}\r\n\r\n{4}'.format(
            request.method,
            request.path,
            request.host,
            request.header,
            request.body
        )
        sock.sendall(bytes(message, encoding='utf-8'))
        result = sock.recv(10000)
        while len(result) > 0:
            print(result)
            result = sock.recv(10000)
