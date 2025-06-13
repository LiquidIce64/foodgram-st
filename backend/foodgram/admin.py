from django.contrib import admin

from . import models

admin.site.register(models.Profile)
admin.site.register(models.Subscription)
admin.site.register(models.Ingredient)
admin.site.register(models.Recipe)
admin.site.register(models.Favorite)
admin.site.register(models.ShoppingCartItem)
