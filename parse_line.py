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
                        nargs='*')
    parser.add_argument('--headers', '-hd',
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
        '\r\n'.join(parse_content(namespace.body)),
        parse_content(namespace.headers),
        namespace.timeout
    ]


def parse_content(content):
    if not content:
        return []
    elif len(content) == 1:
        return [content[0][1:-1]]
    _content = []
    _part = None
    try:
        for part in content:
            if part.endswith('"') and part[-2] != '/':
                _part += ' ' + part
                _part = delete_slashes(_part)
                _content.append(_part[1:-1])
            elif part.startswith('"'):
                _part = part
            else:
                _part += ' ' + part
    except ValueError:
        print('something wrong with content')
    return _content


def delete_slashes(string):
    shielding = ['\'', '/"']
    for char in shielding:
        if char == '\'':
            string = string.replace(char, "'")
        else:
            string = string.replace(char, '"')
    return string
