from django.contrib import admin

from . import models


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'
    list_display = ['username', 'email', 'avatar']
    fieldsets = [(None, {'fields': ['avatar']})]
    search_fields = ('user__username', 'user__email')

    @admin.display(description='Имя пользователя')
    def username(self, obj):
        return obj.user.username

    @admin.display(description='Адрес электронной почты')
    def email(self, obj):
        return obj.user.email

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscribed_to']
    search_fields = ('user__username', 'subscribed_to__username')


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    search_fields = ('name',)


@admin.register(models.RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'ingredient', 'amount', 'measurement_unit']
    search_fields = ('recipe__name', 'ingredient__name')

    @admin.display(description='Единица измерения')
    def measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author_name']
    search_fields = ('name', 'author__username')

    @admin.display(description='Автор')
    def author_name(self, obj):
        return obj.author.username


@admin.register(models.Favorite, models.ShoppingCartItem)
class UserRecipeListAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'recipe']
    search_fields = ('user__username', 'recipe__name')
