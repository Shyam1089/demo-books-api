import unittest
from mock import Mock

from flask_api import status

import api.utils as utils
from api.application import app


class UtilsTest(unittest.TestCase):

    def test_error_handler(self):
        with app.test_request_context():
            @utils.error_handler()
            def temp():
                raise InternalServerError()
            res = temp()
            self.assertEqual(res.status_code, 500)


    def test_error_handler_404_not_found(self):
        with app.test_request_context():
            @utils.error_handler()
            def temp():
                raise utils.BookDoesNotExist("1")
            res = temp()
            self.assertEqual(res.status_code, 404)


    def test_append_trace_headers(self):
        func = Mock()
        func.headers = {'request-id':'123'}
        func.status_code = 200
        decorator = utils.append_json_headers()
        with app.test_request_context() as req:
            return_headers = dict(req.request.headers)
            return_headers.update({'request-id':'123'})
            req.request.headers = return_headers
            response = decorator(lambda x: x)(func)
        self.assertEqual(response.headers, {'request-id': '123'})


    def test_append_json_headers_with_additional_headers(self):
        func = Mock()
        func.headers = {'request-id': '123'}
        func.status_code = 200
        decorator = utils.append_json_headers(additional_headers={'traceid': '456'})
        with app.test_request_context():
            response = decorator(lambda x: x)(func)
        self.assertEqual(response.headers, {'request-id': '123', 'traceid': '456'})


