from collections import OrderedDict

from rest_framework import exceptions, views
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter as DRFDefaultRouter

from drf_swagger_extras.schemas import SchemaGenerator

# Django 1.10 moves .core.urlresolvers to .urls
try:
    from django.urls import NoReverseMatch
except ImportError:
    from django.core.urlresolvers import NoReverseMatch


class DefaultRouter(DRFDefaultRouter):
    """
    Return a view to use as the API root.
    """
    def get_api_root_view(self, api_urls=None):
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

            view_renderers = list(self.root_renderers)
            schema_media_types = []

            if api_urls and self.schema_title:
                view_renderers += list(self.schema_renderers)
                schema_generator = SchemaGenerator(
                    title=self.schema_title,
                    url=self.schema_url,
                    patterns=api_urls
                )
            schema_media_types = [
                renderer.media_type
                for renderer in self.schema_renderers
            ]

        class APIRoot(views.APIView):
            _ignore_model_permissions = True
            renderer_classes = view_renderers

            def get(self, request, *args, **kwargs):
                if request.accepted_renderer.media_type in schema_media_types:
                    # Return a schema response.
                    schema = schema_generator.get_schema(request)
                    if schema is None:
                        raise exceptions.PermissionDenied()
                    return Response(schema)

                # Return a plain {"name": "hyperlink"} response.
                ret = OrderedDict()
                namespace = request.resolver_match.namespace
                for key, url_name in api_root_dict.items():
                    if namespace:
                        url_name = namespace + ':' + url_name
                    try:
                        ret[key] = reverse(
                            url_name,
                            args=args,
                            kwargs=kwargs,
                            request=request,
                            format=kwargs.get('format', None)
                        )
                    except NoReverseMatch:
                        # Don't bail out if eg. no list routes exist,
                        # only detail routes.
                        continue

                return Response(ret)

        return APIRoot.as_view()
