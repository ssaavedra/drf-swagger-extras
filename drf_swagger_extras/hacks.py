"""
Monkey-patch openapi_codec to include our additional elements from
enhanced coreapi.
"""
from openapi_codec import encode


def get_responses(link):
    """Returns documented responses based on the @responds decorator.

    In case no documentation exists, the empty object is returned,
    instead of a default, which better represents that behavior not to
    be formally documented.

    """
    if hasattr(link, '_responses'):
        return link._responses

    return {}


# We need to patch get_operation if we want openapi to also give us
# the opportunity to speak about different return formats.
def get_operation(tag, link):
    return {
        'tags': [tag],
        'description': link.description,
        'responses': encode._get_responses(link),
        'produces': get_produces(link),
        'parameters': encode._get_parameters(link.fields)
    }


def get_produces(link):
    if hasattr(link, '_produces'):
        return link._produces


def monkey_patch():
    encode._get_responses = get_responses
    encode._get_operation = get_operation
