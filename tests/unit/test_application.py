import unittest
import mock
import json
import os
from unittest.mock import patch
from functools import wraps
from flask_api import status

from flask import Flask, request

from api.application import app
import api.utils as utils
import api.application as v1


# Creating a test db
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "Testbooks.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

with app.app_context():
    v1.db.create_all()



class ViewsTest(unittest.TestCase):

    sample_book = {
        "name": "Book",
        "isbn":"1234-4343-4345",
        "authors":"John DOe", 
        "country":"India",
        "number_of_pages":34,
        "publisher":"Oxford",
        "release_date":"20-12-2016"
    }
    expected_keys = ["data", "status", "status_code"]

    @patch("api.application.request")
    def test_create_book_with_valid_json(self, mock_request):
        with app.app_context():
            mock_request.get_json.return_value = self.sample_book
            result = v1.create_book_record()
            resp = json.loads(result.get_data())
            self.assertEqual(set(resp.keys()), set(self.expected_keys))
            self.assertEqual(result.status_code, 201)

    @patch("api.application.request")
    def test_create_book_with_invalid_json(self, mock_request):
        with app.app_context():
            mock_request.get_json.return_value = {"name":"Sample"}
            result = v1.create_book_record()
            resp = json.loads(result.get_data())
            self.assertEqual(result.status_code, 400)
            self.assertEqual(set(resp.keys()), set(["status", "errorDescription", "fields"]))

    @patch("api.application.request")
    def test_create_book_with_invalid_integer(self, mock_request):
        with app.app_context():
            mock_request.get_json.return_value = 123
            result = v1.create_book_record()
            self.assertEqual(result.status_code, 400)


    @patch("api.application.request")
    def test_fetch_books(self, mock_request):
        with app.app_context():
            mock_request.get_json.return_value = {}
            result = v1.fetch_books(None)
            self.assertEqual(result.status_code, 200)


    @patch("api.application.request")
    def test_fetch_books_with_id(self, mock_request):
        with app.app_context():
            mock_request.get_json.return_value = self.sample_book
            create = v1.create_book_record()
            result = v1.fetch_books(1)
            self.assertEqual(result.status_code, 200)

    @patch("api.application.request")
    def test_fetch_books_with_404_not_found(self, mock_request):
        with app.app_context():
            mock_request.get_json.return_value = {}
            self.assertRaises(utils.BookDoesNotExist, v1.fetch_books, 9999999)


    @patch("api.application.request")
    def test_update_book_valid_json(self, mock_request):
        with app.app_context():
            mock_request.get_json.return_value = self.sample_book
            create = v1.create_book_record()
            result = v1.update_book(1)
            self.assertEqual(result.status_code, 200)

    @patch("api.application.request")
    def test_update_book_invalid_json(self, mock_request):
        with app.app_context():
            mock_request.get_json.return_value = self.sample_book
            create = v1.create_book_record()
            mock_request.get_json.return_value = 123
            result = v1.update_book(1)
            self.assertEqual(result.status_code, 400)


    @patch("api.application.request")
    def test_delete_book_valid_json(self, mock_request):
        with app.app_context():
            mock_request.get_json.return_value = self.sample_book
            v1.create_book_record()
            create = v1.fetch_books(None)
            resp = json.loads(create.get_data())
            book_ids = [book.get('id') for book in resp["data"]]
            book_id = int(book_ids[-1])
            result = v1.delete_book_record(book_id)
            self.assertEqual(result.status_code, 200)


    @patch("api.application.request")
    @patch("api.fire_ice_api.get_books")
    def test_fetch_books_from_api(self, mock_get_books, mock_request):
        with app.app_context():
            mock_get_books.return_value = 200, []
            result = v1.get_books_data_from_api()
            resp = json.loads(result.get_data())
            self.assertEqual(set(resp.keys()), set(self.expected_keys))
            self.assertEqual(result.status_code, 200)

    @patch("api.application.request")
    @patch("api.fire_ice_api.get_books")
    def test_fetch_books_from_api_with_fail_code(self, mock_get_books, mock_request):
        with app.app_context():
            mock_get_books.return_value = 301, {}
            result = v1.get_books_data_from_api()
            self.assertEqual(result.status_code, 301)
