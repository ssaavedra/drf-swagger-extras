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
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from drf_swagger_extras.decorators import responds
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

    @responds(200, "Always", schema_name='custom_action')
    @detail_route(methods=['post'], serializer_class=AnotherSerializer)
    def custom_action(self, request, pk):
        "custom_action comment"
        return super(ExampleSerializer, self).retrieve(self, request)

    @list_route()
    def custom_list_action(self, request):
        "custom_list_action comment"
        return super(ExampleViewSet, self).list(self, request)

    def get_serializer(self, *args, **kwargs):
        return super(ExampleViewSet, self).get_serializer(*args, **kwargs)


@responds(500, "On server failure",
          schema={
              ('details', 'norequired'): 'string',
              'required-details': {
                  ('key', 'required'): []
              }
          })
@responds(200, "Always", schema={})
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
urlpatterns = [url(r'^', include(router.urls))]
urlpatterns2 = [
    url(r'^example-view/$', ExampleView.as_view(), name='example-view'),
]


@unittest.skipUnless(coreapi, 'coreapi is not installed')
@override_settings(ROOT_URLCONF='tests.test_schemas')
class TestDecoratorSchemaWorks(TestCase):
    def test_decorator_wrong_schema_obj_element(self):
        self.assertRaises(Exception,
                          responds,
                          500,
                          "On server failure",
                          schema={
                              'wrong-element': APIView,
                          })

    def test_decorator_status_default(self):

        @responds(None, "Test", schema={})
        class TestView(APIView):
            def get(self, request, *args, **kwargs):
                "Example get comment"
                return Response()

        schema_generator = SchemaGenerator(
            title='Test View',
            patterns=[url('^/different-example/$',
                          TestView.as_view(),
                          name='example')]
        )
        schema = generate_swagger_object(schema_generator.get_schema())
        expected = {
            'info': {'title': 'Test View', 'version': ''}, 'host': '',
            'swagger': '2.0',
            'paths': {
                '/different-example/': {
                    'get': {
                        'description': '', 'parameters': [],
                        'tags': ['different-example'],
                        'produces': ['application/json', 'application/xml'],
                        'responses': {'default': {'description': 'Test'}}
                    }
                }
            }
        }

        self.assertEquals(schema, expected)


@unittest.skipUnless(coreapi, 'coreapi is not installed')
@override_settings(ROOT_URLCONF='tests.test_schemas')
class TestReturnsDecorator(TestCase):

    def test_nondecorated_view_works(self):
        class TestView(APIView):
            def get(self, request, *args, **kwargs):
                "Example get comment"
                return Response()

        schema_generator = SchemaGenerator(
            title='Test View',
            patterns=[url('^/different-example/$',
                          TestView.as_view(),
                          name='example')]
        )

        schema = generate_swagger_object(schema_generator.get_schema())

        print(schema)

        expected = {
            'swagger': '2.0',
            'host': '',
            'info': {
                'title': 'Test View',
                'version': ''
            },
            'paths': {
                '/different-example/': {
                    'get': {
                        'tags': ['different-example'],
                        'description': '',
                        'parameters': [],
                        'responses': None,
                        'produces': ['application/json', 'application/xml']
                    }
                }
            }
        }
        self.assertEquals(schema, expected)

    def test_coreapi_schema_compatible(self):
        schema_generator = SchemaGenerator(
            title='Test View', patterns=urlpatterns2)
        schema = schema_generator.get_schema()
        expected = coreapi.Document(
            url='',
            title='Test View',
            content={
                'example-view': {
                    'create': coreapi.Link(
                        url='/example-view/',
                        action='post',
                        description=description_format(ExampleView.__doc__,
                                                       None, ),
                        fields=[]),
                    'read': coreapi.Link(
                        url='/example-view/',
                        action='get',
                        description=description_format(ExampleView.__doc__,
                                                       None, ),
                        fields=[])
                }
            })
        self.assertEquals(schema, expected)

    def test_openapi_has_info_apiview(self):
        schema_generator = SchemaGenerator(
            title='Test View', patterns=urlpatterns2)
        schema = generate_swagger_object(schema_generator.get_schema())

        expected = {
            'info': {
                'version': '', 'title': 'Test View'
            },
            'host': '', 'swagger': '2.0',
            'paths': {
                '/example-view/': {
                    'post': {
                        'parameters': [],
                        'produces': ['application/json', 'application/xml'],
                        'description': 'Example big comment',
                        'tags': ['example-view'],
                        'responses': {
                            200: {'description': 'Always'},
                            500: {
                                'schema': {
                                    'required': ['required-details'],
                                    'properties': {
                                        'details': {'type': 'string'},
                                        'required-details': {
                                            'required': ['key'],
                                            'properties': {
                                                'key': {'type': 'list'}
                                            },
                                            'title': None,
                                            'type': 'object'
                                        }
                                    },
                                    'title': None,
                                    'type': 'object'
                                },
                                'description': 'On server failure'
                            }
                        }
                    },
                    'get': {
                        'parameters': [],
                        'produces': ['application/json', 'application/xml'],
                        'description': 'Example big comment',
                        'tags': ['example-view'],
                        'responses': {
                            200: {'description': 'Always'},
                            500: {
                                'schema': {
                                    'required': ['required-details'],
                                    'properties': {
                                        'details': {'type': 'string'},
                                        'required-details': {
                                            'required': ['key'],
                                            'properties': {
                                                'key': {'type': 'list'}
                                            },
                                            'title': None,
                                            'type': 'object'
                                        }
                                    },
                                    'title': None,
                                    'type': 'object'
                                },
                                'description': 'On server failure'
                            }
                        }
                    }
                }
            }
        }

        print(schema)
        self.assertEquals(schema, expected)

    def test_openapi_has_info_viewset(self):
        schema_generator = SchemaGenerator(
            title='Test View', patterns=urlpatterns)
        schema = generate_swagger_object(schema_generator.get_schema())

        expected = {
            'host': '',
            'swagger': '2.0',
            'info': {
                'title': 'Test View',
                'version': ''
            },
            'paths': {
                '/example/custom_list_action/': {
                    'get': {
                        'responses': None,
                        'tags': ['example'],
                        'description':
                        'custom_list_action comment\n' +
                        'Example ViewSet big comment',
                        'produces': ['application/json', 'application/xml'],
                        'parameters': []
                    }
                },
                '/example/':
                {'get': {
                    'responses': None,
                    'tags': ['example'],
                    'description': 'Example ViewSet big comment',
                    'produces': ['application/json', 'application/xml'],
                    'parameters': [
                        {
                            'required': False,
                            'description': '',
                            'type': 'string',
                            'in': 'query',
                            'name': 'page'
                        }, {
                            'required': False,
                            'description': '',
                            'type': 'string',
                            'in': 'query',
                            'name':
                            'ordering'
                        }
                    ]},
                 'post': {
                     'responses': None,
                     'tags': ['example'],
                     'description': 'Example ViewSet big comment',
                     'produces': ['application/json', 'application/xml'],
                     'parameters': [
                         {
                             'required': True,
                             'description': 'A field description',
                             'type': 'string',
                             'in': 'formData',
                             'name': 'a'
                         }, {
                             'required': False,
                             'description': '',
                             'type': 'string',
                             'in': 'formData',
                             'name': 'b'
                         }
                     ]}},
                '/example/{pk}/custom_action/': {
                    'post': {
                        'responses': {
                            200: {'schema_name': 'custom_action',
                                  'description': 'Always'}
                        },
                        'tags': ['example'],
                        'description':
                        'custom_action comment\nExample ViewSet big comment',
                        'produces': ['application/json', 'application/xml'],
                        'parameters': [
                            {
                                'required': True,
                                'description': '',
                                'type': 'string',
                                'in': 'path',
                                'name': 'pk'
                            }, {
                                'required': True,
                                'description': '',
                                'type': 'string',
                                'in': 'formData',
                                'name': 'c'
                            }, {
                                'required': False,
                                'description': '',
                                'type': 'string',
                                'in': 'formData',
                                'name': 'd'
                            }
                        ]
                    }
                },
                '/example/{pk}/':
                {
                    'get': {
                        'responses': None,
                        'tags': ['example'],
                        'description': 'Example ViewSet big comment',
                        'produces': ['application/json', 'application/xml'],
                        'parameters': [
                            {'required': True,
                             'description': '',
                             'type': 'string',
                             'in': 'path',
                             'name': 'pk'}
                        ]
                    },
                    'delete': {
                        'responses': None,
                        'tags': ['example'],
                        'description': 'Example ViewSet big comment',
                        'produces':
                        ['application/json', 'application/xml'],
                        'parameters': [
                            {'required': True,
                             'description': '',
                             'type': 'string',
                             'in': 'path',
                             'name': 'pk'}
                        ]
                    },
                    'patch': {
                        'responses': None,
                        'tags': ['example'],
                        'description': 'Example ViewSet big comment',
                        'produces': ['application/json', 'application/xml'],
                        'parameters': [
                            {'required': True,
                             'description': '',
                             'type': 'string',
                             'in': 'path',
                             'name': 'pk'},
                            {'required': False,
                             'description':
                             'A field description',
                             'type': 'string',
                             'in': 'formData',
                             'name': 'a'},
                            {'required': False,
                             'description': '',
                             'type': 'string',
                             'in': 'formData',
                             'name': 'b'}
                        ]
                    },
                    'put': {
                        'responses': None,
                        'tags': ['example'],
                        'description': 'Example ViewSet big comment',
                        'produces': ['application/json', 'application/xml'],
                        'parameters': [
                            {'required': True,
                             'description': '',
                             'type': 'string',
                             'in': 'path',
                             'name': 'pk'},
                            {'required': True,
                             'description': 'A field description',
                             'type': 'string',
                             'in': 'formData',
                             'name': 'a'},
                            {'required': False,
                             'description': '',
                             'type': 'string',
                             'in': 'formData',
                             'name': 'b'}
                        ]
                    }
                }
            }
        }

        self.assertEquals(schema, expected)
