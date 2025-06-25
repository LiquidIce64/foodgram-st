from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.dispatch import receiver


MIN_AMOUNT_VALUE = 1
MAX_AMOUNT_VALUE = 32000


User = get_user_model()
User._meta.ordering = ['id']


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='profile', verbose_name='Пользователь')

    avatar = models.ImageField(
        upload_to='users/', null=True, blank=True, verbose_name='Аватар')

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'Профили'
        ordering = ['user__id']

    def __str__(self):
        return f'Профиль {self.user.username}'


@receiver(models.signals.post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscriptions', verbose_name='Пользователь')

    subscribed_to = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscribers', verbose_name='Подписан на')

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['user__id', 'subscribed_to__id']

    def __str__(self):
        user1 = self.user.username
        user2 = self.subscribed_to.username
        return f'Подписка {user1} на {user2}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128, verbose_name='Название')

    measurement_unit = models.CharField(
        max_length=64, verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes', verbose_name='Автор')

    name = models.CharField(
        max_length=256, verbose_name='Название')

    image = models.ImageField(
        upload_to='recipes/', verbose_name='Изображение')

    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_AMOUNT_VALUE),
            MaxValueValidator(MAX_AMOUNT_VALUE)
        ],
        verbose_name='Время готовки (в минутах)')

    text = models.TextField(
        verbose_name='Описание')

    date_posted = models.DateTimeField(
        auto_now_add=True, verbose_name='Время публикации')

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-date_posted']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='recipe_ingredients', verbose_name='Ингредиент')

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredients', verbose_name='Рецепт')

    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_AMOUNT_VALUE),
            MaxValueValidator(MAX_AMOUNT_VALUE)
        ],
        verbose_name='Количество')

    class Meta:
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        ordering = ['-recipe__date_posted', 'ingredient__name']

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name}'


class ShoppingCartItem(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_cart', verbose_name='Пользователь')

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='in_shopping_carts', verbose_name='Рецепт')

    class Meta:
        verbose_name = 'предмет корзины'
        verbose_name_plural = 'Предметы корзин'
        ordering = ['user__id', '-recipe__date_posted']

    def __str__(self):
        return f'Корзина {self.user.username} - {self.recipe.name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites', verbose_name='Пользователь')

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorites', verbose_name='Рецепт')

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранные'
        ordering = ['user__id', '-recipe__date_posted']

    def __str__(self):
        return f'Избранное {self.user.username} - {self.recipe.name}'
