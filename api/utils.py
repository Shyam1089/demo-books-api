import io
import os
import json
from functools import wraps

from flask import request, make_response
from flask_api import status


def append_json_headers(additional_headers: dict = None):
    def decorator(route_function):
        @wraps(route_function)
        def decorated_route(*args, **kwargs):
            r: Response = route_function(*args, **kwargs)
            return_headers = dict(r.headers)
            if additional_headers is not None:
                for ah in additional_headers:
                    return_headers[ah] = additional_headers[ah]
            r.headers = return_headers
            return r
        return decorated_route
    return decorator


def error_handler():
    def decorate(function):
        @wraps(function)
        def call_method(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except BookDoesNotExist as e:
                return make_response(json.dumps({"status": e.type, "errorDescription": e.description}), status.HTTP_404_NOT_FOUND)
            except Exception as e:
                print (str(e))
                return make_response(json.dumps({"status": "error", "errorDescription": "Internal Error Occured!"}), status.HTTP_500_INTERNAL_SERVER_ERROR)
        return call_method
    return decorate



class BookDoesNotExist(Exception):
    def __init__(self, book_id):
        self.type = 'notFound'
        self.description = f'Book with ID: {book_id} does not exists'
