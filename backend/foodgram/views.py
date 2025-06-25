from django.db.models import QuerySet, aggregates, Q
from django.http import HttpResponse
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ModelViewSet, ReadOnlyModelViewSet,
    GenericViewSet, mixins
)

from . import models, serializers, filters, permissions


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
        return (
            models.User.objects
            .filter(subscribers__user=self.request.user)
        )

    def create(self, request, id, *args, **kwargs):
        subscribed_to = get_object_or_404(models.User, pk=id)
        queryset = (
            request.user.subscriptions
            .filter(subscribed_to=subscribed_to)
        )

        if (
            subscribed_to == self.request.user
            or queryset.exists()
        ):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        instance = models.Subscription.objects.create(
            user=request.user, subscribed_to=subscribed_to)
        serializer = self.get_serializer(instance=instance.subscribed_to)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, id, *args, **kwargs):
        subscribed_to = get_object_or_404(models.User, pk=id)
        queryset = (
            request.user.subscriptions
            .filter(subscribed_to=subscribed_to)
        )

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
    permission_classes = (permissions.AdminAuthorOrReadOnly,)


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

        serializer = serializers.RecipeMinifiedSerializer(
            instance=recipe, context={'request': self.request})
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
        recipes = models.Recipe.objects.filter(
            in_shopping_carts__user=request.user)

        filter_arg = Q(recipe_ingredients__recipe__in=recipes)

        ingredients = (
            models.Ingredient.objects
            .filter(filter_arg)
            .annotate(total_sum=aggregates.Sum(
                'recipe_ingredients__amount', filter=filter_arg))
            .values_list('name', 'measurement_unit', 'total_sum')
        )

        file_content = '\n'.join([
            f"{name} ({unit}) - {amount}"
            for name, unit, amount in ingredients
        ])

        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="Shopping list.txt"'
        )
        return response
