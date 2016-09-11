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

        return coreapi.Link(
            url=urlparse.urljoin(self.url, path),
            action=method.lower(),
            encoding=encoding,
            description=description,
            fields=fields,
            transform=None,  # Not handled, but here for future reference
        )

    def get_description(self, path, method, callback, view):
        if hasattr(callback, 'actions'):
            action_name = callback.actions[method.lower()]
            action = (getattr(view, action_name))
            if action.__doc__:
                return self._get_description(view, action)

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
