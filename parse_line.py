import argparse
import re


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
                        default=[''])
    parser.add_argument('--header', '-hd',
                        help='type the header of request',
                        nargs='*')
    return Request(parser.parse_args())


class Request:
    def __init__(self, namespace):
        self.host, self.path = self.parse_uri(namespace.uri[0])
        self.method = self.parse_method(namespace.method[0])
        self.body = self.parse_body(namespace.body)
        self.header = self.parse_header(namespace.header)

    @staticmethod
    def parse_uri(uri):
        path = '/'
        if re.search(r'http://', uri):
            uri = uri[7:]
        host = uri.split('/')[0]
        if '/' in uri:
            path = uri[len(host):]
        return host, path

    @staticmethod
    def parse_method(method):
        methods = ['GET', 'POST', 'PUT', 'HEAD']
        if method not in methods:
            raise ValueError('inputted method is incorrect')
        return method

    @staticmethod
    def parse_body(body):
        return body[0]

    @staticmethod
    def parse_header(header):
        if not header:
            return ''
        return '\r\n'.join(header)
