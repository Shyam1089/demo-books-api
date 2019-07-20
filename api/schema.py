from copy import deepcopy

import marshmallow
from marshmallow import Schema, fields

class createBookRecord(Schema):
    name = fields.String(required=True)
    isbn = fields.String()
    authors = fields.String(required=True)
    country = fields.String()
    number_of_pages = fields.Integer()
    publisher = fields.String()
    release_date = fields.String()


def validate_input_json(data):
    try:
        createBookRecord().load(data)
        return False, data
    except marshmallow.exceptions.ValidationError as e:
        error = deepcopy(e.messages)
        error = {key: " ,".join(value) for (key, value) in error.items() if isinstance(value, list)}
        print (error)
        print ("*"*40)
        return True, error
