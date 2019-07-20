import json
import unittest
from unittest.mock import patch

import api.fire_ice_api as fire_ice_api
from api.application import app

class FireApiTest(unittest.TestCase):

    # Unit test for get_books()
    @patch.object(fire_ice_api.requests, 'get')
    def test_get_books(self, mock_requests_get):
        mock_requests_get.return_value.content.decode.return_value = '{"name":"A Clash of Kings"}'
        with app.test_request_context():
            status_code, res = fire_ice_api.get_books({"name":"A Clash of Kings"})
            self.assertEqual(res, (json.loads(mock_requests_get.return_value.content.decode.return_value)))
