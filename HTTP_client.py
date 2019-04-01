from parse_line import create_parser
import request

if __name__ == '__main__':
    parser = create_parser()
    request.send_request(parser)
