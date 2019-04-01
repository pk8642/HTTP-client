from parse_line import create_request
import send_request

if __name__ == '__main__':
    request = create_request()
    send_request.send(request)
