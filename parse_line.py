import argparse


def create_parser():
    parser = argparse.ArgumentParser(
        prog='HTTP client',
        description='''This is a client for receiving and sending data via
        HTTP protocol'''
    )
    parser.add_argument('uri',
                        metavar='web-address',
                        help='gets URI to request',
                        nargs=1)
    parser.add_argument('--method', '-m',
                        help='type the method of request'
                             '{GET|PUT|POST|HEAD|OPTIONS|DELETE}',
                        nargs='?',
                        default='GET')
    parser.add_argument('--body', '-b',
                        help='type the body of request',
                        nargs='*',
                        default=[''])
    parser.add_argument('--header', '-hd',
                        help='type the header of request between "',
                        nargs='*')
    parser.add_argument('--timeout', '-to',
                        help='set the timeout of waiting response',
                        nargs='?',
                        type=float,
                        default=15)
    return parser


def convert_to_list(namespace):
    return [
        namespace.uri[0],
        namespace.method,
        namespace.body[0],
        parse_header(namespace.header),
        namespace.timeout
    ]


def parse_header(header):
    if not header:
        return ''
    return '\r\n'.join(header)
