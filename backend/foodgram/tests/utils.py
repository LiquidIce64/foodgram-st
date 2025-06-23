from rest_framework import status
from rest_framework.test import APITestCase
from drf_extra_fields.fields import Base64ImageField

from foodgram import models


class APIResponseTestCase(APITestCase):
    def assert_response(
        self, url, method='get',
        login_as=None,
        data=None,
        expected_status=status.HTTP_200_OK,
        expected_struct=None,
        expected_data=None,
        debug_log=False
    ):
        if login_as is not None:
            self.client.force_authenticate(login_as)
        func = getattr(self.client, method)
        if data is None:
            response = func(url)
        else:
            response = func(url, data)
        if debug_log:
            print(f'''
-----------------------------------
{url} ({method})
request data: {data}
expected: {expected_status}, {expected_data}
got: {response.status_code}, {response.data}
-----------------------------------
''')
        self.assertEqual(response.status_code, expected_status)
        if expected_struct is not None:
            self.assert_struct(response.data, expected_struct)
        if expected_data is not None:
            for k, v in expected_data.items():
                self.assertEqual(response.data.get(k), v)
        return response

    def assert_invalid_data(self, url, data, method='post', login_as=None):
        for key in data.keys():
            test_data = data.copy()
            test_data.pop(key)
            self.assert_response(
                url, method=method,
                login_as=login_as,
                data=test_data,
                expected_status=status.HTTP_400_BAD_REQUEST)

    def assert_struct(self, data, expected_structure: type | list | dict):
        if isinstance(expected_structure, type):
            self.assertIsInstance(data, expected_structure)
        elif isinstance(expected_structure, dict):
            self.assertIsInstance(data, dict)
            for key, expected in expected_structure.items():
                self.assertIn(key, data)
                self.assert_struct(data[key], expected)
        elif isinstance(expected_structure, list):
            self.assertIsInstance(data, list)
            for item in data:
                self.assert_struct(item, expected_structure[0])


TEST_IMAGE_DATA = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA\
AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVK\
w4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='


def create_user(username):
    user = models.User(
        email=f'{username}@example.com',
        username=username,
        first_name='test',
        last_name='user',
        is_active=True
    )
    user.set_password('foodgram_test')
    user.save()
    return user


def create_recipe(name, author):
    image = Base64ImageField().to_internal_value(TEST_IMAGE_DATA)
    recipe = models.Recipe.objects.create(
        author=author, name=name, image=image,
        text='test recipe', cooking_time=1
    )
    models.RecipeIngredient.objects.create(
        recipe=recipe, amount=1,
        ingredient=models.Ingredient.objects.get(pk=1)
    )
    return recipe


def get_user_json_short(id=None, username=None, user=None):
    if user is not None:
        id = user.pk
        username = user.username
    return {
        'id': id,
        'email': f'{username}@example.com',
        'username': username,
        'first_name': 'test',
        'last_name': 'user'
    }


def get_user_json(id=None, username=None, user=None,
                  subscribed=False, avatar='', **kwargs):
    res = get_user_json_short(id, username, user)
    res.update(
        is_subscribed=subscribed,
        avatar=avatar,
        **kwargs
    )
    return res


def get_ingredient_json(ingredient=None, id=None, **kwargs):
    if id is not None:
        ingredient = models.Ingredient.objects.get(pk=id)
    res = {
        'id': ingredient.pk,
        'name': ingredient.name,
        'measurement_unit': ingredient.measurement_unit
    }
    res.update(**kwargs)
    return res


def get_recipe_json_short(recipe):
    image = (
        'http://testserver' +
        Base64ImageField().to_representation(recipe.image)
    )
    return {
        'id': recipe.pk,
        'name': recipe.name,
        'image': image,
        'cooking_time': recipe.cooking_time
    }


def get_recipe_json(recipe, user=None):
    res = get_recipe_json_short(recipe)
    res.update(
        text=recipe.text,
        author=get_user_json(user=recipe.author),
        is_favorited=(
            user is not None
            and user.favorites.filter(recipe=recipe).exists()
        ),
        is_in_shopping_cart=(
            user is not None
            and user.shopping_cart.filter(recipe=recipe).exists()
        ),
        ingredients=[
            get_ingredient_json(r_ing.ingredient, amount=r_ing.amount)
            for r_ing in recipe.ingredients.all()
        ]
    )
    return res
