from django.shortcuts import resolve_url
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ModelViewSet, GenericViewSet, mixins
)

from . import models, serializers, filters


class AvatarViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    serializer_class = serializers.AvatarSerializer

    def get_object(self):
        return self.request.user.profile


class RecipeViewSet(ModelViewSet):
    queryset = models.Recipe.objects
    serializer_class = serializers.RecipeSerializer
    filter_backends = (filters.RecipeFilterBackend,)


class RecipeLinkView(APIView):
    def get(self, request, id, *args, **kwargs):
        get_object_or_404(models.Recipe, pk=id)
        return Response({
            'short-link': resolve_url('short-link', id=id)
        })
