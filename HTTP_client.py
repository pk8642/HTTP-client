from parse_line import create_parser
import request

if __name__ == '__main__':
    parser = create_parser()
    my_request = request.Request(parser)
    print(my_request.send_request())
