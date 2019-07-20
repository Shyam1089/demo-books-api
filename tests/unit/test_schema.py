import json
import unittest
from unittest.mock import patch

import api.schema as schema
from api.application import app

class SchemaTest(unittest.TestCase):

	def test_validate_input_json_with_missing_input(self):
		input_json = {"name":"Test"}
		status, response = schema.validate_input_json(input_json)
		expected_result = {'authors': 'Missing data for required field.'}
		self.assertEqual(set(response.keys()), set(expected_result.keys()))


	def test_validate_input_json_with_all_input(self):
		input_json = {"name":"Test", "authors": "author"}
		status, response = schema.validate_input_json(input_json)
		expected_result = {"name":"Test", "authors": "author"}
		self.assertEqual(set(response.keys()), set(expected_result.keys()))
