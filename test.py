import unittest
import parse_line
import send_request


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

    def check_args(self, args):
        testing_req = parse_line.Request(args)
        self.assertEqual(testing_req.host, args['uri'][0])
        self.assertEqual(testing_req.path, args['uri'][1])
        self.assertEqual(testing_req.method, args['method'])
        self.assertEqual(testing_req.body, args['body'])
        self.assertEqual(testing_req.header, args['header'])

    def check_parsing_input(self, line_input):
        parser = parse_line.create_parser()
        args = parser.parse_args(self.parse_args(line_input))
        self.check_args(parse_line.convert_to_dict(args))

    def test_correct_args(self):
        uri = 'example.org'
        args = {
            'uri': parse_line.parse_uri(uri),
            'method': 'GET',
            'body': 'some body',
            'header': 'Content-type: text/html'
        }
        self.check_args(args)

    def test_correct_args_two(self):
        uri = 'www.cyberforum.ru/python-network/thread1911394.html'
        args = {
            'uri': parse_line.parse_uri(uri),
            'method': 'GET',
            'body': 'another sample of body',
            'header': ['header 1', 'header2', 'header3']
        }
        self.check_args(args)

    def test_correct_input(self):
        line = '-u example.com -m GET'
        self.check_parsing_input(line)

    def test_correct_input_two(self):
        line = '-u www.cyberforum.ru/python/ ' \
               '-m GET -b "some body once told me that world is gonna roll ' \
               'me" -hd "Content-Type: text"'
        self.check_parsing_input(line)

    def test_incorrect_input_method(self):
        line = '-u example.com -m GE'
        with self.assertRaises(ValueError):
            self.check_parsing_input(line)

    def test_incorrect_input_uri(self):
        line = '-u https://github.com -m GET'
        with self.assertRaises(ValueError):
            self.check_parsing_input(line)

    def test_incorrect_input_uri(self):
        line = '-u www.cyber'


if __name__ == '__main__':
    unittest.main()
