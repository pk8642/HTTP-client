import parse_line
import send_request

if __name__ == '__main__':
    parser = parse_line.create_parser()
    args = parse_line.convert_to_dict(parser.parse_args())
    request = send_request.Request(args)
    request.send()
