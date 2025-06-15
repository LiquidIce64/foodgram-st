from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views

router_root = SimpleRouter()
router_root.register(
    'recipes', views.RecipeViewSet, basename='recipe')
router_root.register(
    'ingredients', views.IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('users/me/avatar/', views.AvatarViewSet.as_view(
        {'put': 'update', 'delete': 'destroy'}), name='avatar'),
    path('users/subscriptions/', views.SubscriptionViewSet.as_view(
        {'get': 'list'}), name='subscriptions'),
    path('users/<id>/subscribe/', views.SubscriptionViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'}), name='subscribe'),

    path('recipes/download_shopping_cart/',
         views.DownloadShoppingCartView.as_view(),
         name='download_shopping_cart'),
    path('recipes/<id>/get-link/',
         views.RecipeLinkView.as_view(), name='get-short-link'),
    path('recipes/<id>/favorite/',
         views.FavoriteView.as_view(), name='favorite_recipe'),
    path('recipes/<id>/shopping_cart/',
         views.ShoppingCartView.as_view(), name='shopping_cart'),

    path('', include(router_root.urls)),

    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
