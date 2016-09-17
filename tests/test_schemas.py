"""
Tests for schema generation.
"""
import unittest

from django.conf.urls import include, url
from django.test import TestCase, override_settings
from rest_framework import filters, pagination, permissions, serializers
from rest_framework.compat import coreapi
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator as BaseSchemaGenerator
from rest_framework.test import APIClient
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from drf_swagger_extras.routers import DefaultRouter
from drf_swagger_extras.schemas import SchemaGenerator, description_format
from openapi_codec.encode import generate_swagger_object


class MockUser(object):
    def is_authenticated(self):
        return True


class ExamplePagination(pagination.PageNumberPagination):
    page_size = 100


class ExampleSerializer(serializers.Serializer):
    a = serializers.CharField(required=True, help_text='A field description')
    b = serializers.CharField(required=False)
    read_only = serializers.CharField(read_only=True)
    hidden = serializers.HiddenField(default='hello')


class AnotherSerializer(serializers.Serializer):
    c = serializers.CharField(required=True)
    d = serializers.CharField(required=False)


class ExampleViewSet(ModelViewSet):
    "Example ViewSet big comment"
    pagination_class = ExamplePagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    serializer_class = ExampleSerializer

    @detail_route(methods=['post'], serializer_class=AnotherSerializer)
    def custom_action(self, request, pk):
        "custom_action comment"
        return super(ExampleSerializer, self).retrieve(self, request)

    @list_route()
    def custom_list_action(self, request):
        "custom_list_action comment"
        return super(ExampleViewSet, self).list(self, request)

    def get_serializer(self, *args, **kwargs):
        assert self.request
        assert self.action
        return super(ExampleViewSet, self).get_serializer(*args, **kwargs)


class ExampleView(APIView):
    "Example big comment"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        "Example get comment"
        return Response()

    def post(self, request, *args, **kwargs):
        "Example post comment"
        return Response()


router = DefaultRouter(schema_title='Example API' if coreapi else None)
router.register('example', ExampleViewSet, base_name='example')
urlpatterns = [
    url(r'^', include(router.urls))
]
urlpatterns2 = [
    url(r'^example-view/$', ExampleView.as_view(), name='example-view')
]


@unittest.skipUnless(coreapi, 'coreapi is not installed')
@override_settings(ROOT_URLCONF='tests.test_schemas')
class TestRouterGeneratedSchema(TestCase):
    def test_anonymous_request(self):
        client = APIClient()
        response = client.get('/', HTTP_ACCEPT='application/vnd.coreapi+json')
        self.assertEqual(response.status_code, 200)
        expected = coreapi.Document(
            url='',
            title='Example API',
            content={
                'example': {
                    'list': coreapi.Link(
                        url='/example/',
                        action='get',
                        fields=[
                            coreapi.Field('page',
                                          required=False,
                                          location='query'),
                            coreapi.Field('ordering',
                                          required=False,
                                          location='query'),
                        ],
                        description=description_format(
                            ExampleViewSet.__doc__,
                            None,
                        ),
                    ),
                    'custom_list_action': coreapi.Link(
                        url='/example/custom_list_action/',
                        action='get',
                        description=description_format(
                            ExampleViewSet.__doc__,
                            ExampleViewSet.custom_list_action.__doc__
                        ),
                    ),
                    'retrieve': coreapi.Link(
                        url='/example/{pk}/',
                        action='get',
                        fields=[
                            coreapi.Field('pk', required=True, location='path')
                        ],
                        description=description_format(
                            ExampleViewSet.__doc__,
                            None,
                        ),
                    )
                }
            }
        )

        self.assertEqual(response.data.data['example']['list'],
                         expected.data['example']['list'])

        self.assertEqual(
            response.data.data['example']['custom_list_action'].description,
            expected.data['example']['custom_list_action'].description
        )

        self.assertEqual(response.data.data['example']['retrieve'],
                         expected.data['example']['retrieve'])

        self.assertEqual(response.data, expected)

    def test_authenticated_request(self):
        client = APIClient()
        client.force_authenticate(MockUser())
        response = client.get('/', HTTP_ACCEPT='application/vnd.coreapi+json')
        self.assertEqual(response.status_code, 200)
        expected = coreapi.Document(
            url='',
            title='Example API',
            content={
                'example': {
                    'list': coreapi.Link(
                        url='/example/',
                        action='get',
                        description=description_format(
                            ExampleViewSet.__doc__,
                            None,
                        ),
                        fields=[
                            coreapi.Field('page',
                                          required=False,
                                          location='query'),
                            coreapi.Field('ordering',
                                          required=False,
                                          location='query')
                        ]
                    ),
                    'create': coreapi.Link(
                        url='/example/',
                        action='post',
                        encoding='application/json',
                        description=description_format(
                            ExampleViewSet.__doc__,
                            None,
                        ),
                        fields=[
                            coreapi.Field('a',
                                          required=True,
                                          location='form',
                                          description='A field description'),
                            coreapi.Field('b',
                                          required=False,
                                          location='form')
                        ]
                    ),
                    'retrieve': coreapi.Link(
                        url='/example/{pk}/',
                        action='get',
                        description=description_format(
                            ExampleViewSet.__doc__,
                            None,
                        ),
                        fields=[
                            coreapi.Field('pk', required=True, location='path')
                        ]
                    ),
                    'custom_action': coreapi.Link(
                        url='/example/{pk}/custom_action/',
                        action='post',
                        encoding='application/json',
                        description=description_format(
                            ExampleViewSet.__doc__,
                            ExampleViewSet.custom_action.__doc__,
                        ),
                        fields=[
                            coreapi.Field('pk',
                                          required=True,
                                          location='path'),
                            coreapi.Field('c',
                                          required=True,
                                          location='form'),
                            coreapi.Field('d',
                                          required=False,
                                          location='form'),
                        ]
                    ),
                    'custom_list_action': coreapi.Link(
                        url='/example/custom_list_action/',
                        description=description_format(
                            ExampleViewSet.__doc__,
                            ExampleViewSet.custom_list_action.__doc__,
                        ),
                        action='get'
                    ),
                    'update': coreapi.Link(
                        url='/example/{pk}/',
                        action='put',
                        encoding='application/json',
                        description=description_format(
                            ExampleViewSet.__doc__,
                            None,
                        ),
                        fields=[
                            coreapi.Field('pk',
                                          required=True,
                                          location='path'),
                            coreapi.Field('a',
                                          required=True,
                                          location='form',
                                          description='A field description'),
                            coreapi.Field('b', required=False, location='form')
                        ]
                    ),
                    'partial_update': coreapi.Link(
                        url='/example/{pk}/',
                        action='patch',
                        encoding='application/json',
                        description=description_format(
                            ExampleViewSet.__doc__,
                            None,
                        ),
                        fields=[
                            coreapi.Field('pk',
                                          required=True,
                                          location='path'),
                            coreapi.Field('a',
                                          required=False,
                                          location='form',
                                          description='A field description'),
                            coreapi.Field('b', required=False, location='form')
                        ]
                    ),
                    'destroy': coreapi.Link(
                        url='/example/{pk}/',
                        action='delete',
                        description=description_format(
                            ExampleViewSet.__doc__,
                            None,
                        ),
                        fields=[
                            coreapi.Field('pk', required=True, location='path')
                        ]
                    )
                }
            }
        )
        self.assertEqual(response.data, expected)


@unittest.skipUnless(coreapi, 'coreapi is not installed')
class TestSchemaGenerator(TestCase):
    def test_view(self):
        schema_generator = SchemaGenerator(title='Test View',
                                           patterns=urlpatterns2)
        schema = schema_generator.get_schema()
        expected = coreapi.Document(
            url='',
            title='Test View',
            content={
                'example-view': {
                    'create': coreapi.Link(
                        url='/example-view/',
                        action='post',
                        description=description_format(
                            ExampleView.__doc__,
                            None,
                        ),
                        fields=[]
                    ),
                    'read': coreapi.Link(
                        url='/example-view/',
                        action='get',
                        description=description_format(
                            ExampleView.__doc__,
                            None,
                        ),
                        fields=[]
                    )
                }
            }
        )
        self.assertEquals(schema, expected)

    def test_base_generator(self):
        """Avoid regressions on BaseSchemaGenerator due to monkey-patching"""
        schema_generator = BaseSchemaGenerator(title='Test View',
                                               patterns=urlpatterns2)
        schema = generate_swagger_object(schema_generator.get_schema())
        expected = generate_swagger_object(coreapi.Document(
            url='',
            title='Test View',
            content={
                'example-view': {
                    'create': coreapi.Link(
                        url='/example-view/',
                        action='post',
                        fields=[]
                    ),
                    'read': coreapi.Link(
                        url='/example-view/',
                        action='get',
                        fields=[]
                    )
                }
            }
        ))

        self.assertEquals(schema, expected)
