import unittest
from unittest import mock, TestCase
import parse_line
import HTTP_client
from request import Request
from response import Response
import io


class TestArguments(TestCase):
    @staticmethod
    def parse_args(line):
        args_array = line.split()
        result = []
        temp = ''
        for e in args_array:
            if len(temp) > 0:
                temp += f' {e}'
                if '"' in e:
                    result.append(temp[:-1])
                    temp = ''
            else:
                if '"' in e:
                    temp = e[1:]
                else:
                    result.append(e)
        return result

    def check_args(self, args, host=None):
        if host:
            _host, _ = HTTP_client.parse_uri(args[0])
            self.assertEqual(_host, host)
        testing_req = Request(None, None, *args[1:])
        self.assertEqual(testing_req._method, args[1])
        self.assertEqual(testing_req._body, args[2])
        self.assertEqual(testing_req._headers, args[3])

    def check_parsing_input(self, line_input, host=None):
        parser = parse_line.create_parser()
        args = parser.parse_args(self.parse_args(line_input))
        self.check_args(parse_line.convert_to_list(args), host)

    def test_correct_args(self):
        uri = 'example.org'
        args = [
            uri,
            'GET',
            'some body',
            'Content-type: text/html'
        ]
        self.check_args(args)

    def test_correct_args_two(self):
        uri = 'www.cyberforum.ru/python-network/thread1911394.html'
        args = [
            uri,
            'GET',
            'another sample of body',
            ['header 1', 'header2', 'header3']
        ]
        self.check_args(args)

    def test_correct_input(self):
        line = 'example.com -m GET'
        self.check_parsing_input(line)

    def test_correct_input_two(self):
        line = 'www.cyberforum.ru/python/ ' \
               '-m GET -b "some body once told me that world is gonna roll ' \
               'me" -hd "Content-Type: text"'
        self.check_parsing_input(line)

    def test_incorrect_input_method(self):
        line = 'example.com -m GE'
        with self.assertRaises(ValueError):
            self.check_parsing_input(line, 'example.com')

    def test_incorrect_input_uri(self):
        line = 'https://github.com -m GET'
        with self.assertRaises(ValueError):
            self.check_parsing_input(line, 'github.com')


class TestFunctionalityResponse(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response = Response(self.get_fake_socket(b''))

    def clear_response(self):
        self.response.response_headers = ''
        self.response.response_body = b''

        self.response.headers = {}  # i.e. 'Content-Type: text/html'
        self.response.cookies = []  # cookie pairs

        self.response.filename = None
        self.response.ext = 'html'
        self.response.charset = None
        self.response.connection = True

    @staticmethod
    def get_fake_reader(text):
        return io.BytesIO(text)

    @staticmethod
    def get_fake_socket(text):
        sock = mock.Mock()
        sock.makefile.return_value = io.BytesIO(text)
        return sock

    def test_receive_headers(self):
        text = b'HTTP-code\r\nHeader: value\r\n\r\n'
        self.response.receive_headers(self.get_fake_reader(text))

        self.assertEqual(self.response.headers,
                         {
                             'code': 'HTTP-code\r\n',
                             'header': 'value\r\n'
                         })
        self.assertEqual(self.response.response_headers,
                         'Header: value\r\n')
        self.clear_response()

    def test_getting_cookie(self):
        text = b'code\r\nSet-Cookie: cookie\r\n\r\n'
        self.response.receive_headers(self.get_fake_reader(text))

        self.assertEqual(self.response.cookies, ['cookie\r\n'])
        self.clear_response()

    def test_getting_multiple_cookies(self):
        text = b'code\r\nSet-Cookie: cookie1\r\nSet-Cookie: cookie2\r\n\r\n'
        self.response.receive_headers(self.get_fake_reader(text))

        self.assertEqual(self.response.cookies, ['cookie1\r\n', 'cookie2\r\n'])
        self.clear_response()

    def test_getting_filename_from_filepath(self):
        path = 'www.example.com/some-file.some-ext'
        self.response.get_filename(path)

        self.assertEqual((self.response.filename, self.response.ext),
                         ('some-file', 'some-ext'))
        self.clear_response()

    def test_getting_filename_from_html(self):
        path = 'www.example.com/some-page'
        self.response.response_body = b'tatata<title>Title of the page</title>'
        self.response.charset = 'utf8'
        self.response.get_filename(path)

        self.assertEqual((self.response.filename, self.response.ext),
                         ('Title of the page', 'html'))
        self.clear_response()

    def test_not_getting_filename(self):
        path = 'www.bad-path.com/'
        self.response.response_body = b'very bad body'
        self.response.charset = 'utf8'
        self.response.get_filename(path)

        self.assertEqual((self.response.filename, self.response.ext),
                         ('received', 'html'))
        self.clear_response()

    def test_static_recv(self):
        text = b'abrakadabra'
        reader = self.get_fake_reader(text)
        self.response.static_recv(reader, len(text))

        self.assertEqual(self.response.response_body, text)
        self.clear_response()

    def test_dynamic_recv(self):
        text = b'8\r\n12345678\r\n0\r\n\r\n'
        reader = self.get_fake_reader(text)
        self.response.dynamic_recv(reader)

        self.assertEqual(self.response.response_body, b'12345678')
        self.clear_response()

    def test_full_receive_with_handled_headers(self):
        text = b'HTTP 200 OK\r\nHeader: value\r\nContent-Type: text/html; ' \
               b'charset=utf8\r\nContent-Length: 14\r\nConnection: close' \
               b'\r\n\r\nsome body text'
        self.response.sock = self.get_fake_socket(text)

        self.response.receive()

        self.assertEqual(self.response.charset, 'utf8\r\n')
        self.assertEqual(self.response.connection, False)
        self.assertEqual(self.response.ext, 'html')
        self.assertEqual(len(self.response.response_body), 14)

    def test_full_receive_without_handled_headers(self):
        text = b'HTTP 200 OK\r\nHeader: value\r\nTransfer-Encoding: chunked' \
               b'\r\n\r\nE\r\nsome body text\r\n0\r\n\r\n'
        self.response.sock = self.get_fake_socket(text)

        self.response.receive()

        self.assertEqual(len(self.response.response_body), 14)

if __name__ == '__main__':
    unittest.main()
