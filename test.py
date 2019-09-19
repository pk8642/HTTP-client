import unittest
import parse_line
import request
import  HTTP_client


class Test(unittest.TestCase):
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
        testing_req = request.Request(None, None, *args[1:])
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


if __name__ == '__main__':
    unittest.main()
