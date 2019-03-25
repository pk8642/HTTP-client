from parse_line import create_parser
import request

if __name__ == '__main__':
    args = create_parser()
    my_request = request.Request(args)
    print(my_request.send_request())
