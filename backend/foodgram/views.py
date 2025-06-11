from django.db.models import QuerySet, aggregates
from django.http import HttpResponse
from rest_framework import status
from rest_framework.reverse import reverse
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
            'short-link': reverse('short-link', id=id, request=request)
        })


class ShoppingCartView(APIView):
    def post(self, request, id, *args, **kwargs):
        recipe = get_object_or_404(models.Recipe, pk=id)
        if request.user.shopping_cart.filter(recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        models.ShoppingCartItem.objects.create(
            user=request.user, recipe=recipe)

        serializer = serializers.RecipeMinifiedSerializer(instance=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id, *args, **kwargs):
        recipe = get_object_or_404(models.Recipe, pk=id)
        queryset = request.user.shopping_cart.filter(recipe=recipe)
        if not queryset.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartView(APIView):
    def get(self, request, *args, **kwargs):
        shopping_cart: QuerySet = request.user.shopping_cart
        ingredients = (
            shopping_cart
            .values(r_ing='recipe__ingredients')
            .values(
                ing_name='r_ing__ingredient__name',
                ing_unit='r_ing__ingredient__measurement_unit',
                ing_amount=aggregates.Sum('r_ing__amount')
            )
            .values_list('ing_name', 'ing_unit', 'ing_amount')
        )

        file_content = '\n'.join([
            f"{name} ({unit}) - {amount}"
            for name, unit, amount in ingredients
        ])

        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="Shopping list.txt"'
        return response
