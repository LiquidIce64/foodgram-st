from django.db.models import QuerySet, aggregates
from django.http import HttpResponse
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ModelViewSet, ReadOnlyModelViewSet,
    GenericViewSet, mixins
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


class SubscriptionViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = serializers.SubscriptionSerializer

    def get_queryset(self):
        return self.request.user.subscriptions.select_related('subscribed_to')

    def create(self, request, id, *args, **kwargs):
        subscribed_to = get_object_or_404(models.User, pk=id)

        if (
            subscribed_to == self.request.user or
            self.request.user.subscriptions.filter(
                subscribed_to=subscribed_to).exists()
        ): return Response(status=status.HTTP_400_BAD_REQUEST)

        instance = models.Subscription.objects.create(
            user=request.user, subscribed_to=subscribed_to)
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, id, *args, **kwargs):
        subscribed_to = get_object_or_404(models.User, pk=id)
        queryset = request.user.subscriptions.filter(subscribed_to=subscribed_to)
        if not queryset.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    pagination_class = None
    filter_backends = (filters.NameSearchFilter,)
    permission_classes = (AllowAny,)


class RecipeViewSet(ModelViewSet):
    queryset = models.Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    filter_backends = (filters.RecipeFilterBackend,)
    permission_classes = (IsAuthenticatedOrReadOnly,)


class RecipeLinkView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, id, *args, **kwargs):
        get_object_or_404(models.Recipe, pk=id)
        return Response({
            'short-link': reverse('short-link', args=(id,), request=request)
        })


class AddRemoveRecipeView(APIView):
    def get_queryset(self, request) -> QuerySet:
        raise NotImplementedError

    def post(self, request, id, *args, **kwargs):
        recipe = get_object_or_404(models.Recipe, pk=id)
        queryset = self.get_queryset(request).filter(recipe=recipe)
        if queryset.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        queryset.create(
            user=request.user, recipe=recipe)

        serializer = serializers.RecipeMinifiedSerializer(instance=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id, *args, **kwargs):
        recipe = get_object_or_404(models.Recipe, pk=id)
        queryset = self.get_queryset(request).filter(recipe=recipe)
        if not queryset.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteView(AddRemoveRecipeView):
    def get_queryset(self, request) -> QuerySet:
        return request.user.favorites


class ShoppingCartView(AddRemoveRecipeView):
    def get_queryset(self, request) -> QuerySet:
        return request.user.shopping_cart


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
