from jsonschema import validate


class Validator(object):
    def __init__(self, schema):
        self.schema = schema

    def validate(self, obj):
        validate(obj, schema=self.schema)


register_user = Validator({
    '$schema': 'http://json-schema.org/schema#',
    'type': 'object',
    'properties': {
        'username': {'type': 'string', 'pattern': '[a-z_]+'},
        'password': {'type': 'string'},
        'full_name': {'type': 'string'}
    },
    'required': ['username', 'password', 'full_name']
})


auth = Validator({
    '$schema': 'http://json-schema.org/schema#',
    'type': 'object',
    'properties': {
        'username': {'type': 'string', 'pattern': '[a-z_]+'},
        'password': {'type': 'string'}
    },
    'required': ['username', 'password']
})
