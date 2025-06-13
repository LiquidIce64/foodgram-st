from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import (
    UserSerializer as BaseUserSerializer,
    UserCreateSerializer as BaseUserCreateSerializer
)

from . import models


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = (
            'id', 'username', 'email',
            'first_name', 'last_name',
            'is_subscribed', 'avatar',
        )
        read_only_fields = ('username',)
        required = ('email', 'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and user.subscriptions.filter(subscribed_to=obj).exists()

    def get_avatar(self, obj):
        try:
            return obj.profile.avatar.url
        except ValueError:
            return ""


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta:
        model = models.User
        fields = (
            'username', 'password', 'email',
            'first_name', 'last_name',
        )
        required = ('email', 'first_name', 'last_name')

    def perform_create(self, validated_data):
        user = super().perform_create(validated_data)
        models.Profile.objects.create(user=user)
        return user


class AvatarSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    avatar = Base64ImageField()

    class Meta:
        model = models.Profile
        fields = ('user', 'avatar')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects)
    name = serializers.CharField(
        read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True, source='ingredient.measurement_unit')

    class Meta:
        model = models.RecipeIngredient
        fields = (
            'id', 'amount',
            'name', 'measurement_unit'
        )


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)

    class Meta:
        model = models.Recipe
        fields = (
            'id', 'author', 'name', 'image',
            'ingredients', 'cooking_time', 'text',
            'is_favorited', 'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.shopping_cart.filter(recipe=obj).exists()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        validated_data['author'] = self.context['request'].user
        recipe = models.Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            models.RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['id'],  # Since id is a PKRelatedField, this is an Ingredient object
                amount=ingredient_data['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().update(instance, validated_data)

        ingredient_mapping = {r_ing.ingredient.pk: r_ing for r_ing in recipe.ingredients.all()}
        data_mapping = {data['id'].pk: data for data in ingredients_data}

        for ingredient_id, data in data_mapping.items():
            ingredient = ingredient_mapping.get(ingredient_id, None)
            if ingredient is None:
                models.RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=data['id'],
                    amount=data['amount']
                )
            else:
                ingredient.update(amount=data['amount'])

        for ingredient_id, ingredient in ingredient_mapping.items():
            if ingredient_id not in data_mapping:
                ingredient.delete()

        return recipe


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only = '__all__'


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = (
            'id', 'username', 'email',
            'first_name', 'last_name',
            'is_subscribed', 'avatar',
            'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit', None)
        recipes = obj.recipes.order_by('-date_posted')
        if limit is not None:
            recipes = recipes[:int(limit)]
        return RecipeMinifiedSerializer(instance=recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
