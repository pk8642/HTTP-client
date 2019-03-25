import argparse


def create_parser():
    parser = argparse.ArgumentParser(
        prog='HTTP client',
        description='''This is a client for receiving and sending data via
        HTTP protocol'''
    )
    parser.add_argument('--uri', '-u',
                        help='gets URI to request',
                        nargs=1,
                        default='example.org')
    parser.add_argument('--method', '-m',
                        help='type the method of request',
                        nargs=1,
                        default='GET')
    parser.add_argument('--body', '-b',
                        help='type the body of request',
                        nargs='*',
                        default='')
    parser.add_argument('--header', '-hd',
                        help='type the header of request',
                        nargs='*',
                        default='')
    return parse_namespace(parser.parse_args())


def parse_uri(uri):
    host = uri.split('/')[0]
    path = ''
    return host, path


def parse_method(method):
    return method


def parse_body(body):
    return body


def parse_header(header):
    return header


def parse_namespace(namespace):
    host, path = parse_uri(namespace.uri)
    method = parse_method(namespace.method)
    body = parse_body(namespace.body)
    header = parse_header(namespace.header)
    return host, path, method, body, header
