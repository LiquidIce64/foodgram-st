from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views


router_root = SimpleRouter()
router_root.register('recipes', views.RecipeViewSet, basename='recipe')

router_profile = SimpleRouter()
router_profile.register('avatar', views.AvatarViewSet, basename='avatar')


urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    path('', include(router_root.urls)),
    path('users/me/', include(router_profile.urls)),

    path('recipes/<id>/get-link/', views.RecipeLinkView.as_view(), name='get-short-link')
]
