from __future__ import unicode_literals

from django.conf.urls import include, url
from django.db import models
from django.test import TestCase
from rest_framework import serializers, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from drf_swagger_extras.routers import DefaultRouter

factory = APIRequestFactory()


class RouterTestModel(models.Model):
    uuid = models.CharField(max_length=20)
    text = models.CharField(max_length=200)


class NoteSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='routertestmodel-detail',
        lookup_field='uuid'
    )

    class Meta:
        model = RouterTestModel
        fields = ('url', 'uuid', 'text')


class NoteViewSet(viewsets.ModelViewSet):
    queryset = RouterTestModel.objects.all()
    serializer_class = NoteSerializer
    lookup_field = 'uuid'


class KWargedNoteViewSet(viewsets.ModelViewSet):
    queryset = RouterTestModel.objects.all()
    serializer_class = NoteSerializer
    lookup_field = 'text__contains'
    lookup_url_kwarg = 'text'


class MockViewSet(viewsets.ModelViewSet):
    queryset = None
    serializer_class = None


namespaced_router = DefaultRouter()
namespaced_router.register(r'example', MockViewSet, base_name='example')

urlpatterns = [
    url(r'^non-namespaced/', include(namespaced_router.urls)),
    url(r'^namespaced/', include(namespaced_router.urls, namespace='example'))
]


class BasicViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        return Response({'method': 'list'})

    @detail_route(methods=['post'])
    def action1(self, request, *args, **kwargs):
        return Response({'method': 'action1'})

    @detail_route(methods=['post'])
    def action2(self, request, *args, **kwargs):
        return Response({'method': 'action2'})

    @detail_route(methods=['post', 'delete'])
    def action3(self, request, *args, **kwargs):
        return Response({'method': 'action2'})

    @detail_route()
    def link1(self, request, *args, **kwargs):
        return Response({'method': 'link1'})

    @detail_route()
    def link2(self, request, *args, **kwargs):
        return Response({'method': 'link2'})


class TestNameableRoot(TestCase):
    def setUp(self):
        class NoteViewSet(viewsets.ModelViewSet):
            queryset = RouterTestModel.objects.all()

        self.router = DefaultRouter()
        self.router.root_view_name = 'nameable-root'
        self.router.register(r'notes', NoteViewSet)
        self.urls = self.router.urls

    def test_router_has_custom_name(self):
        expected = 'nameable-root'
        self.assertEqual(expected, self.urls[-1].name)
