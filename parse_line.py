import argparse
import re


def create_request():
    parser = argparse.ArgumentParser(
        prog='HTTP client',
        description='''This is a client for receiving and sending data via
        HTTP protocol'''
    )
    parser.add_argument('--uri', '-u',
                        help='gets URI to request',
                        nargs=1)
    parser.add_argument('--method', '-m',
                        help='type the method of request',
                        nargs=1)
    parser.add_argument('--body', '-b',
                        help='type the body of request',
                        nargs='*',
                        default=[''])
    parser.add_argument('--header', '-hd',
                        help='type the header of request',
                        nargs='*')
    return convert_to_dict(parser.parse_args())


def convert_to_dict(namespace):
    return {
        'uri': parse_uri(namespace.uri[0]),
        'method': parse_method(namespace.method[0]),
        'body': parse_body(namespace.body),
        'header': parse_header(namespace.header)
    }


def parse_uri(uri):
    path = '/'
    if re.search(r'http://', uri):
        uri = uri[7:]
    host = uri.split('/')[0]
    if '/' in uri:
        path = uri[len(host):]
    return host, path


def parse_method(method):
    methods = ['GET', 'POST', 'PUT', 'HEAD']
    if method not in methods:
        raise ValueError('inputted method is incorrect')
    return method


def parse_body(body):
    return body[0]


def parse_header(header):
    if not header:
        return ''
    return '\r\n'.join(header)


class Request:
    def __init__(self, **args):
        self.host, self.path = args['uri']
        self.method = args['method']
        self.body = args['body']
        self.header = args['header']
