import unittest
import parse_line
import send_request


class Test(unittest.TestCase):
    def correct_args(self, args):
        testing_req = parse_line.Request(args)
        self.assertEqual(testing_req.host, args['uri'][0])
        self.assertEqual(testing_req.path, args['uri'][1])
        self.assertEqual(testing_req.method, args['method'])
        self.assertEqual(testing_req.body, args['body'])
        self.assertEqual(testing_req.header, args['header'])

    def test_correct_args(self):
        uri = 'example.org'
        args = {
            'uri': parse_line.parse_uri(uri),
            'method': 'GET',
            'body': 'some body',
            'header': 'Content-type: text/html'
        }
        self.correct_args(args)

    def test_correct_args_two(self):
        uri = 'www.cyberforum.ru/python-network/thread1911394.html'
        args = {
            'uri': parse_line.parse_uri(uri),
            'method': 'GET',
            'body': 'another sample of body',
            'header': ['header 1', 'header2', 'header3']
        }
        self.correct_args(args)


if __name__ == '__main__':
    unittest.main()
