import unittest
import parse_line
import send_request


class Test(unittest.TestCase):
    @staticmethod
    def create_test_case(**args):
        return parse_line.Request(**args)

    def test_correct_args(self):
        args = {
            'uri': ['example.org', '/'],
            'method': 'GET',
            'body': 'some body',
            'header': 'Content-type: text/html'
        }
        testing_req = Test.create_test_case(**args)
        self.assertEqual(testing_req.host, 'example.org')
        self.assertEqual(testing_req.path, '/')
        self.assertEqual(testing_req.method, 'GET')
        self.assertEqual(testing_req.body, 'some body')
        self.assertEqual(testing_req.header, 'Content-type: text/html')
