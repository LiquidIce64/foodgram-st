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
        return (
            user.is_authenticated
            and user.subscriptions.filter(subscribed_to=obj).exists()
        )

    def get_avatar(self, obj):
        try:
            return obj.profile.avatar.url
        except Exception:
            return ''


class UserCreateSerializer(BaseUserCreateSerializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    class Meta:
        model = models.User
        fields = (
            'id', 'username', 'password', 'email',
            'first_name', 'last_name',
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        email = attrs.get('email')
        if models.User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'email is already in use'}
            )
        return super().validate(attrs)


class AvatarSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    avatar = Base64ImageField()

    class Meta:
        model = models.Profile
        fields = ('user', 'avatar')


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
        return RecipeMinifiedSerializer(
            instance=recipes,
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects, source='ingredient')
    name = serializers.CharField(
        read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True, source='ingredient.measurement_unit')
    amount = serializers.IntegerField(
        min_value=models.MIN_AMOUNT_VALUE, max_value=models.MAX_AMOUNT_VALUE)

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
    cooking_time = serializers.IntegerField(
        min_value=models.MIN_AMOUNT_VALUE, max_value=models.MAX_AMOUNT_VALUE)

    class Meta:
        model = models.Recipe
        fields = (
            'id', 'author', 'name', 'image',
            'ingredients', 'cooking_time', 'text',
            'is_favorited', 'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.shopping_cart.filter(recipe=obj).exists()
        )

    @staticmethod
    def set_ingredients(instance, ingredients_data):
        instance.ingredients.bulk_create([
            models.RecipeIngredient(recipe=instance, **data)
            for data in ingredients_data
        ])

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        validated_data['author'] = self.context['request'].user
        recipe = super().create(validated_data)
        self.set_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().update(instance, validated_data)
        instance.ingredients.all().delete()
        self.set_ingredients(recipe, ingredients_data)
        return recipe


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only = '__all__'
