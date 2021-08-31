# -*- coding: utf-8 -*-
import os
import json

from flask import Flask, jsonify, request, abort, make_response
from flask_api import status
from flask_sqlalchemy import SQLAlchemy

from api import fire_ice_api
from api import utils
from api import schema

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "books.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    books = db.relationship('Book', backref='author')

    def __repr__(self):
        return '<Author:{}>'.format(self.name)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    isbn = db.Column(db.String(64), index=True)
    authors = db.Column(db.Integer, db.ForeignKey('author.id'))
    country = db.Column(db.String(64))
    number_of_pages = db.Column(db.Integer)
    publisher = db.Column(db.String(64))
    release_date = db.Column(db.String(64))

    def __repr__(self):
        return '<Book:{}>'.format(self.name)


with app.app_context():
    db.create_all()


JSON_TYPE_HEADERS = {'Content-Type': 'application/json'}
SUCCESS_RESPONSE = {"status": "success", "status_code": status.HTTP_200_OK }
BOOK_KEYS = ["name", "isbn", "authors",  "number_of_pages", "publisher", "country", "release_date"]


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Requested URL not found.'}), status.HTTP_404_NOT_FOUND)


def get_book_array(row):
    book = {}
    for column in row.__table__.columns:
        book[column.name] = str(getattr(row, column.name))
    book.update({"authors": [Author.query.get(int(book['authors'])).name]})
    return book


def get_book_by_id(book_id):
    book = Book.query.filter_by(id=book_id).first()
    if book is None:
        raise utils.BookDoesNotExist(book_id)
    return book


@app.route('/api/external-books', methods=['GET'])
@utils.append_json_headers(JSON_TYPE_HEADERS)
def get_books_data_from_api():
    args = request.args.copy().to_dict()
    status_code, data = fire_ice_api.get_books(args)
    if status_code != status.HTTP_200_OK:
        return make_response(jsonify(data), status_code)
    resp = SUCCESS_RESPONSE.copy()
    if data:
        data = [{key: book_data.get(key,"") for key in BOOK_KEYS} for book_data in data]
    resp.update({'data': data})
    return make_response(jsonify(resp), status_code)


@app.route('/api/v1/books', methods=['POST'])
@utils.append_json_headers(JSON_TYPE_HEADERS)
def create_book_record():
    try:
        request_json = request.get_json()
        if not isinstance(request_json, dict) or not request_json:
            raise Exception("Invalid Json")
    except:
        request_json = {}

    # Validating input json
    error, data = schema.validate_input_json(request_json)
    if error:
        resp = {'errorDescription': 'Invalid input or missing required field.', "status": "error"}
        resp.update({"fields": data})
        return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

    # Creating Author
    author_data = Author(name=data.get("authors"))
    author_rec = db.session.add(author_data)
    db.session.commit()

    # Creating Book
    book_data = Book(name=data.get("name"), isbn=data.get("isbn", ""), authors=author_data.id, 
        country=data.get("country", ""), number_of_pages=data.get("number_of_pages", ""), 
        publisher=data.get("publisher", ""), release_date=data.get("release_date", "")
    )
    book_rec = db.session.add(book_data)
    db.session.commit()
    
    book_array = get_book_array(book_data)
    book_array.pop("id")
    response = {
        "status_code": status.HTTP_201_CREATED,
        "status": "success",
        "data": [{ 
            "book": book_array
        }]
    }
    return make_response(jsonify(response), status.HTTP_201_CREATED)


@app.route('/api/v1/books', defaults={'rec_id': None}, methods=['GET'])
@app.route('/api/v1/books/<int:rec_id>', methods=['GET'])
@utils.append_json_headers(JSON_TYPE_HEADERS)
def fetch_books(rec_id):
    response = SUCCESS_RESPONSE.copy()
    if rec_id:
        book = get_book_by_id(rec_id)
        response.update({"data": get_book_array(book)})
    else:
        kwargs = request.args.copy().to_dict()
        keys_to_keep = set(kwargs.keys()) - set(["number_of_pages", "isbn", "authors"])
        new_kwargs = {k: v for k, v in kwargs.items() if k in keys_to_keep}
        books = Book.query.filter_by(**new_kwargs)
        data = [get_book_array(book) for book in books]
        response.update({"data": data})
    return make_response(jsonify(response), status.HTTP_200_OK)


@app.route('/api/v1/books/<int:rec_id>', methods=['PATCH'])
@app.route('/api/v1/books/<int:rec_id>/update', methods=['POST'])
@utils.append_json_headers(JSON_TYPE_HEADERS)
@utils.error_handler()
def update_book(rec_id):
    book = get_book_by_id(rec_id)
    try:
        request_json = request.get_json()
        if not isinstance(request_json, dict) or not request_json:
            raise Exception("Empty Json")
    except:
        return make_response(jsonify({"status":"error", "errorDescription": "Invalid input!"}), status.HTTP_400_BAD_REQUEST)

    keys_to_keep = ["number_of_pages", "isbn", "name", "country", "publisher", "release_date"]
    data = {k: v for k, v in request_json.items() if k in keys_to_keep}
    if data:
        updated = Book.query.filter_by(id=rec_id).update(data)
        db.session.commit()
    if "authors" in request_json:
        updated = Author.query.filter_by(id=book.authors).update(dict(name=request_json.get("authors")))
        db.session.commit()
    response = SUCCESS_RESPONSE.copy()
    response.update({
        "message" : f'The book {book.name} was updated successfully.',
        "data": get_book_array(book)
    })
    return make_response(jsonify(response), status.HTTP_200_OK)


@app.route('/api/v1/books/<int:rec_id>', methods=['DELETE'])
@app.route('/api/v1/books/<int:rec_id>/delete', methods=['POST'])
@utils.append_json_headers(JSON_TYPE_HEADERS)
@utils.error_handler()
def delete_book_record(rec_id):
    book = get_book_by_id(rec_id)
    response = SUCCESS_RESPONSE.copy()
    response.update({
        "message" : f'The book {book.name} was deleted successfully.',
        "data": []
    })
    Book.query.filter_by(id=rec_id).delete()
    db.session.commit()
    return make_response(jsonify(response), status.HTTP_200_OK)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
