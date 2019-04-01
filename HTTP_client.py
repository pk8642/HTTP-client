import parse_line
import send_request

if __name__ == '__main__':
    args = parse_line.create_request()
    request = parse_line.Request(**args)
    send_request.send(request)
