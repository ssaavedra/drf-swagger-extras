from copy import copy

from rest_framework.compat import urlparse
from rest_framework.schemas import SchemaGenerator as BaseSchemaGenerator

import coreapi


class SchemaGenerator(BaseSchemaGenerator):
    def get_link(self, path, method, callback, view):
        """
        Return a `coreapi.Link` instance for the given endpoint.
        """
        fields = self.get_path_fields(path, method, callback, view)
        fields += self.get_serializer_fields(path, method, callback, view)
        fields += self.get_pagination_fields(path, method, callback, view)
        fields += self.get_filter_fields(path, method, callback, view)

        if fields and any([field.location in ('form', 'body')
                           for field in fields]):
            encoding = self.get_encoding(path, method, callback, view)
        else:
            encoding = None

        description = self.get_description(path, method, callback, view)

        link = coreapi.Link(
            url=urlparse.urljoin(self.url, path),
            action=method.lower(),
            encoding=encoding,
            description=description,
            fields=fields,
            transform=None,  # Not handled, but here for future reference
        )
        link._responses = self.get_responses(path, method, callback, view)
        link._produces = self.get_produces(path, method, callback, view)

        return link

    def _get_actual_view(self, method, callback, view, default=True):
        if hasattr(callback, 'actions'):
            action_name = callback.actions[method.lower()]
            action = getattr(view, action_name)
            return action
        else:
            return view if default else None

    def get_responses(self, path, method, callback, view):
        # Get generic responses
        responses = {}
        if hasattr(view, '_responses'):
            responses = copy(view._responses)
            pass

        action = self._get_actual_view(method, callback, view, default=False)
        if action and hasattr(action, '_responses'):
            responses.update(action._responses)
        return responses or None

    def get_produces(self, path, method, callback, view):
        return ["application/json", "application/xml"]

    def get_description(self, path, method, callback, view):
        action = self._get_actual_view(method, callback, view, default=False)
        if action and action.__doc__:
            return self._get_description(view, action)
        else:
            return self._get_description(view, None)

    def _get_description(self, view, action=None):
        generic = view.__doc__
        specific = action.__doc__

        return description_format(generic, specific)


def description_format(generic=None, specific=None):
    def unwrap(s):
        if s:
            return "\n".join([l.strip() for l in s.splitlines()])
        else:
            return ''

    if specific:
        specific += "\n\n"

    if generic or specific:
        return "{1}{0}".format(unwrap(generic),
                               unwrap(specific))
