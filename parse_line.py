import argparse


def create_parser():
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
                        default='')
    parser.add_argument('--header', '-hd',
                        help='type the header of request',
                        nargs='*',
                        default='')
    return Parser(parser.parse_args())


class Parser:
    def __init__(self, namespace):
        self.host, self.path = self.parse_uri(namespace.uri[0])
        self.method = self.parse_method(namespace.method[0])
        self.body = self.parse_body(namespace.body)
        self.header = self.parse_header(namespace.header)

    def parse_uri(self, uri):
        host = uri.split('/')[0]
        path = ''
        return host, path

    def parse_method(self, method):
        return method

    def parse_body(self, body):
        return body

    def parse_header(self, header):
        return header

    def parse_namespace(self, namespace):
        host, path = self.parse_uri(namespace.uri)
        method = self.parse_method(namespace.method)
        body = self.parse_body(namespace.body)
        header = self.parse_header(namespace.header)
        return host, path, method, body, header
