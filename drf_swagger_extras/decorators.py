import six
from rest_framework import status


def sanitized(schema_key):
    second_colon = schema_key.find(':', 1)
    if schema_key[0] == ':' and second_colon:
        return schema_key[second_colon + 1:]


def key_params(schema_key):
    second_colon = schema_key.find(':', 1)
    if schema_key[0] == ':' and second_colon:
        return schema_key[1:second_colon]


def get_required(schema_keys):
    for key in schema_keys:
        params = key_params(key)
        if 'norequired' in params:
            continue
        yield sanitized(key)


def get_object_properties(schema):
    return {
        sanitized(skey): val
        for skey, val in schema.items()
    }


def parse_schema(schema):
    if type(schema) is six.binary_type or type(schema) is six.text_type:
        return {
            'type': schema,
        }
    elif type(schema) is list:
        return {
            'type': 'list',
        }
    elif type(schema) is dict:
        title = schema.get(':title', None)
        required_elts = list(get_required(schema.keys()))
        properties = get_object_properties(schema)
        return {
            'type': 'object',
            'title': title,
            'properties': {
                prop_name: parse_schema(subschema)
                for prop_name, subschema in properties.items()
            },
            'required': required_elts,
        }
    else:
        raise Exception('Unsupported schema definition')


def responds(status=status.HTTP_200_OK,
             meaning='Undocumented status code',
             schema=None,
             schema_name=None,
             **kwargs):
    """Documents the status code per handled case.

    Additional parameters may make it into the OpenAPI documentation
    per view. Examples of those parameters include
    examples={'application/json': <example>}. As schemata are needed
    in order to render the examples in the Web UI, an error will be
    signaled if examples= are provided without a schema= parameter.

    Schemas can be easily built using a specific syntax.

    TODO: Document the syntax here

    """
    # TODO: Document syntax in above docstring
    if status is None:
        status = 'default'
    obj = {}
    obj['description'] = meaning

    if schema:
        obj['schema'] = parse_schema(schema)

    if schema_name:
        obj['schema_name'] = schema_name

    obj.update(kwargs)

    def decorator(func):
        # We do not return a decorator function, we just modify
        # in-place our function to have the property that we will look
        # forward later for.
        if not hasattr(func, '_responses'):
            func._responses = {}
        func._responses[status] = obj
        return func
    return decorator
