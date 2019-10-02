import unittest
from unittest import mock, TestCase
import parse_line
import HTTP_client
from request import Request
from response import Response
import io


def get_fake_socket(text=b'', to=15):
    sock = mock.Mock()
    sock.makefile.return_value = io.BytesIO(text)
    sock.sendall.return_value = None
    sock.settimeout.return_value = to
    sock.connect.return_value = None
    sock.close.return_value = None
    return sock


def get_fake_reader(text=b''):
    return io.BytesIO(text)


class TestArguments(TestCase):
    def check_args(self, args, host=None):
        if host:
            _host, _ = HTTP_client.parse_uri(args[0])
            self.assertEqual(_host, host)
        testing_req = Request(None, None, *args[1:])
        self.assertEqual(testing_req.method, args[1])
        self.assertEqual(testing_req.headers, args[2])
        self.assertEqual(testing_req.body, args[3])

    def check_parsing_input(self, line_input, host=None):
        parser = parse_line.create_parser()
        args = parser.parse_args(line_input)
        self.check_args(parse_line.convert_to_list(args), host)

    def test_correct_args(self):
        args = [
            ['example.org'],
            'GET',
            'Content-type: text/html',
            'some body'
        ]
        self.check_args(args)

    def test_correct_args_two(self):
        args = [
            ['www.cyberforum.ru/python-network/thread1911394.html'],
            'GET',
            ['header 1', 'header2', 'header3'],
            'another sample of body'
        ]
        self.check_args(args)

    def test_correct_input(self):
        line = 'example.com -m GET'
        self.check_parsing_input(line.split())

    def test_correct_input_two(self):
        line = 'www.cyberforum.ru/python/ ' \
               '-m GET -b "some body once told me that world is gonna roll ' \
               'me" -hd "Content-Type: text"'
        self.check_parsing_input(line.split())

    def test_incorrect_input_method(self):
        line = 'example.com -m GE'
        with self.assertRaises(ValueError):
            self.check_parsing_input(line.split(), 'example.com')

    def test_incorrect_input_uri(self):
        line = 'https://github.com -m GET'
        with self.assertRaises(ValueError):
            self.check_parsing_input(line.split(), 'github.com')

    def test_parsing_content(self):
        line = 'www.example.com -b "This is /"body/" in" "2 lines"'
        self.check_parsing_input(line.split())


class MockResponse:
    def __init__(self):
        self.sock = None
        self.response_headers = None
        self.response_body = None
        self.headers = None
        self.cookies = None
        self.filename = None
        self.ext = None
        self.charset = None
        self.connection = True

        self.response = Response(get_fake_socket(b''))

    def _set_text_to_sock(self, text, to=15):
        self.response.sock = get_fake_socket(text, to)

    def _get_reader(self, text):
        self._set_text_to_sock(text)
        return self.response.sock.makefile()

    def _set_body(self, text):
        self.response.response_body = text

    def receive_headers(self, text):
        reader = self._get_reader(text)
        self.response.receive_headers(reader)

        self.headers = self.response.headers
        self.response_headers = self.response.response_headers
        self.cookies = self.response.cookies

    def get_filename(self, path):
        self.response.get_filename(path)

        self.filename, self.ext = self.response.filename, self.response.ext

    def static_recv(self, text, length):
        reader = self._get_reader(text)
        self.response.static_recv(reader, length)

        self.response_body = self.response.response_body

    def dynamic_recv(self, text):
        reader = self._get_reader(text)
        self.response.dynamic_recv(reader)

        self.response_body = self.response.response_body

    def receive(self):
        self.response.receive()

        self.headers = self.response.headers
        self.response_headers = self.response.response_headers
        self.cookies = self.response.cookies
        self.response_body = self.response.response_body
        self.charset = self.response.charset


class TestFunctionalityResponse(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response = Response(get_fake_socket(b''))

    def clear_response(self):
        self.response.response_headers = ''
        self.response.response_body = b''

        self.response.headers = {}  # i.e. 'Content-Type: text/html'
        self.response.cookies = []  # cookie pairs

        self.response.filename = None
        self.response.ext = 'html'
        self.response.charset = None
        self.response.connection = True

    def test_receive_headers(self):
        text = b'HTTP-code\r\nHeader: value\r\n\r\n'
        response = MockResponse()
        response.receive_headers(text)

        self.assertEqual(response.headers,
                         {
                             'code': 'HTTP-code\r\n',
                             'header': 'value\r\n'
                         })
        self.assertEqual(response.response_headers,
                         'Header: value\r\n')

    def test_getting_cookie(self):
        text = b'code\r\nSet-Cookie: cookie\r\n\r\n'
        response = MockResponse()
        response.receive_headers(text)

        self.assertEqual(response.cookies, ['cookie\r\n'])

    def test_getting_multiple_cookies(self):
        text = b'code\r\nSet-Cookie: cookie1\r\nSet-Cookie: cookie2\r\n\r\n'
        response = MockResponse()
        response.receive_headers(text)

        self.assertEqual(response.cookies, ['cookie1\r\n', 'cookie2\r\n'])

    def test_getting_filename_from_filepath(self):
        path = 'www.example.com/some-file.some-ext'
        response = MockResponse()
        response.get_filename(path)

        self.assertEqual((response.filename, response.ext),
                         ('some-file', 'some-ext'))

    def test_getting_filename_from_html(self):
        path = 'www.example.com/some-page'
        html = b'tatata<title>Title of the page</title>'
        response = MockResponse()
        response._set_body(html)
        response.response.charset = 'utf8'
        response.get_filename(path)

        self.assertEqual((response.filename, response.ext),
                         ('Title of the page', 'html'))

    def test_not_getting_filename(self):
        path = 'www.bad-path.com/'
        html = b'very bad body'
        response = MockResponse()
        response._set_body(html)
        response.response.charset = 'utf8'
        response.get_filename(path)

        self.assertEqual((response.filename, response.ext),
                         ('received', 'html'))

    def test_static_recv(self):
        text = b'abrakadabra'
        response = MockResponse()
        response.static_recv(text, len(text))

        self.assertEqual(response.response_body, text)
        self.clear_response()

    def test_dynamic_recv(self):
        text = b'8\r\n12345678\r\n0\r\n\r\n'
        response = MockResponse()
        response.dynamic_recv(text)

        self.assertEqual(response.response_body, b'12345678')
        self.clear_response()

    def test_full_receive_with_handled_headers(self):
        text = b'HTTP 200 OK\r\nHeader: value\r\nContent-Type: text/html; ' \
               b'charset=utf8\r\nContent-Length: 14\r\nConnection: close' \
               b'\r\n\r\nsome body text'
        self.response.sock = get_fake_socket(text)

        self.response.receive()

        self.assertEqual(self.response.charset, 'utf8\r\n')
        self.assertEqual(self.response.connection, False)
        self.assertEqual(self.response.ext, 'html')
        self.assertEqual(len(self.response.response_body), 14)

    def test_full_receive_without_handled_headers(self):
        text = b'HTTP 200 OK\r\nHeader: value\r\nTransfer-Encoding: chunked' \
               b'\r\n\r\nE\r\nsome body text\r\n0\r\n\r\n'
        self.response.sock = get_fake_socket(text)

        self.response.receive()

        self.assertEqual(len(self.response.response_body), 14)


class MockRequest:
    def __init__(self):
        self.host = None
        self.path = None
        self.method = None
        self.headers = None
        self.body = None
        self.timeout = None
        self.request = None

    def _create_request(self, host='www.example.com', path='/', method='GET',
                        headers=None, body='', to=15):
        if headers is None:
            headers = []

        self.request = Request(host, path, method, headers, body, to)

    def form_message(self):
        result = self.request.form_message()

        self.headers = self.request.headers
        return result

    def modify_data(self):
        self.request.modify_data()

        self.body = self.request.body
        self.headers = self.request.headers

    def send_data(self, sockets):
        with mock.patch('socket.socket', get_fake_socket):
            return self.request.send_data(sockets)

    def set_cookies(self, cookies):
        self.request.set_cookies(cookies)

        self.headers = self.request.headers


class TestFunctionalityRequest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = None

    # def get_args(self):
    #     return self.args.copy()
    #
    # def prepare_request(self, args):
    #     if self.request is None:
    #         self.request = Request(*args)
    #     else:
    #         attributes = self.request.__dict__
    #         iterator = args.__iter__()
    #         for attribute in attributes[:-1]:
    #             attributes[attribute] = iterator.__next__()

    def test_forming_messages_with_headers(self):
        request = MockRequest()
        request._create_request(headers=['Header: value',
                                         'Another-Header: value'],
                                body='somebody')

        expect = b'GET / HTTP/1.1\r\nHost: www.example.com\r\nHeader: value' \
                 b'\r\nAnother-Header: value\r\n'
        actual = request.form_message()

        self.assertEqual(expect, actual)

    def test_modifying_data_with_body(self):
        headers = ['Access-Encoding: gzip', 'Content-Type: plain/text; '
                                            'charset=utf8']
        body = 'look at me, I\'m body'

        request = MockRequest()
        request._create_request(headers=headers,
                                body=body)

        request.modify_data()

        self.assertEqual(request.headers, [
            'Access-Encoding: gzip',
            'Content-Type: plain/text; charset=utf8',
            f'Content-Length: {len(body)}\r\n'
        ])

    def test_modifying_data_with_no_body(self):
        headers = ['Access-Encoding: gzip', 'Content-Type: plain/text; '
                                            'charset=utf8']
        request = MockRequest()
        request._create_request(headers=headers)

        request.modify_data()

        self.assertEqual(request.headers, [
            'Access-Encoding: gzip',
            'Content-Type: plain/text; charset=utf8\r\n',
        ])

    def test_sending_data_with_existing_socket(self):
        request = MockRequest()
        request._create_request()
        sockets = {request.request.host: get_fake_socket(b'')}

        request.send_data(sockets)

        expected = b'GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\n'
        sockets[request.request.host].sendall.assert_called_with(expected)

    def test_sending_data_with_no_existing_socket(self):
        request = MockRequest()
        request._create_request()

        mock_sock = request.send_data({})

        expected = b'GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\n'
        mock_sock.sendall.assert_called_with(expected)

    def test_setting_cookies(self):
        request = MockRequest()
        request._create_request()

        cookies = {
            'www.example.com': ['some-cookie=value; path=/; '
                                'expires=Mon, 28-Oct-2019 14:24:42 GMT\r\n']
        }

        request.set_cookies(cookies)

        self.assertEqual(request.headers, ['Cookie: some-cookie=value'])


class TestClient(TestCase):
    def test_client_with_base_arguments(self):
        host = 'example.com'
        usr_input = [host, 'n', 'n', 'cls']
        resp = b'HTTP 200 OK\r\nContent-Length: 4\r\n' \
               b'Content-Type: text/html; charset=utf8\r\n' \
               b'\r\nbody\r\n\r\n'

        fake_sock = get_fake_socket(resp)

        with mock.patch('builtins.input', side_effect=usr_input), \
             mock.patch('socket.socket', side_effect=lambda: fake_sock):
            HTTP_client.main()

        fake_sock.connect.assert_called_once()
        fake_sock.sendall.assert_called_with(b'GET / HTTP/1.1\r\nHost: '
                                             b'example.com\r\n\r\n')

    def test_client_with_3xx_exception(self):
        host = 'example.com'
        usr_input = [host, 'y', 'n', 'n', 'cls']
        bad_resp = b'HTTP 301 Moved Permanently\r\n' \
                   b'Location: example.org\r\n\r\n'
        good_resp = b'HTTP 200 OK\r\nContent-Length: 7\r\n' \
                    b'Content-Type: text/html; charset=utf8\r\n' \
                    b'\r\nnot bad\r\n\r\n'
        bad_fake_sock = get_fake_socket(bad_resp)
        good_fake_sock = get_fake_socket(good_resp)
        fake_sockets = [bad_fake_sock,
                        good_fake_sock]

        with mock.patch('builtins.input', side_effect=usr_input), \
             mock.patch('socket.socket', side_effect=fake_sockets):
            HTTP_client.main()

        bad_fake_sock.makefile.assert_called_once()
        bad_fake_sock.close.assert_called_once()
        bad_fake_sock.connect.assert_called_once()
        bad_fake_sock.sendall.assert_called_once()

        good_fake_sock.makefile.assert_called_once()
        good_fake_sock.close.assert_called_once()
        good_fake_sock.connect.assert_called_once()
        good_fake_sock.sendall.assert_called_once()


if __name__ == '__main__':
    unittest.main()
