from .utils import (
    APIResponseTestCase, status, TEST_IMAGE_DATA,
    create_user, create_recipe, get_recipe_json, get_ingredient_json
)
from . import structs


def get_recipe_url(recipe_id):
    return f'/api/recipes/{recipe_id}/'


URL_RECIPES = '/api/recipes/'


RECIPE_CREATE_DATA = {
    'ingredients': [{
        'id': 1,
        'amount': 1
    }],
    'image': TEST_IMAGE_DATA,
    'name': 'test_recipe_4',
    'text': 'test recipe',
    'cooking_time': 1
}

RECIPE_UPDATE_DATA = {
    'ingredients': [{
        'id': 2,
        'amount': 2
    }],
    'name': 'test_recipe_edit',
    'text': 'test recipe',
    'cooking_time': 1
}


class SubscriptionTestCase(APIResponseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = create_user('test_recipe_user_1')
        cls.user2 = create_user('test_recipe_user_2')
        cls.user3 = create_user('test_recipe_user_3')
        cls.recipe1 = create_recipe('test_recipe_1', cls.user1)
        cls.recipe2 = create_recipe('test_recipe_2', cls.user1)
        cls.recipe3 = create_recipe('test_recipe_3', cls.user2)
        cls.user1.favorites.create(user=cls.user1, recipe=cls.recipe1)
        cls.user1.shopping_cart.create(user=cls.user1, recipe=cls.recipe2)

    def test_list(self):
        self.assert_response(
            URL_RECIPES,
            expected_data={
                'results': [
                    get_recipe_json(self.recipe3),
                    get_recipe_json(self.recipe2),
                    get_recipe_json(self.recipe1),
                ]
            })
        self.assert_response(
            URL_RECIPES,
            login_as=self.user1,
            expected_data={
                'results': [
                    get_recipe_json(self.recipe3, self.user1),
                    get_recipe_json(self.recipe2, self.user1),
                    get_recipe_json(self.recipe1, self.user1),
                ]
            })

    def test_detail(self):
        self.assert_response(
            get_recipe_url(self.recipe1.pk),
            expected_data=get_recipe_json(self.recipe1))
        self.assert_response(
            get_recipe_url(self.recipe1.pk),
            login_as=self.user1,
            expected_data=get_recipe_json(self.recipe1, self.user1))

    def test_detail_not_found(self):
        self.assert_response(
            get_recipe_url(99999999),
            expected_status=status.HTTP_404_NOT_FOUND)

    def test_create(self):
        self.assert_response(
            URL_RECIPES, method='post',
            login_as=self.user1,
            data=RECIPE_CREATE_DATA,
            expected_status=status.HTTP_201_CREATED,
            expected_struct=structs.recipe)

    def test_create_invalid(self):
        self.assert_invalid_data(
            URL_RECIPES, RECIPE_CREATE_DATA,
            login_as=self.user1)

    def test_create_no_auth(self):
        self.assert_response(
            URL_RECIPES, method='post',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_update(self):
        expected_data = get_recipe_json(self.recipe1, self.user1) | {
            'name': 'test_recipe_edit',
            'ingredients': [get_ingredient_json(id=2, amount=2)]
        }
        self.assert_response(
            get_recipe_url(self.recipe1.pk), method='patch',
            login_as=self.user1,
            data=RECIPE_UPDATE_DATA,
            expected_data=expected_data)

    def test_update_no_auth(self):
        self.assert_response(
            get_recipe_url(self.recipe1.pk), method='patch',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_update_not_found(self):
        self.assert_response(
            get_recipe_url(99999999), method='patch',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_update_other_users_recipe(self):
        self.assert_response(
            get_recipe_url(self.recipe3.pk), method='patch',
            login_as=self.user1,
            expected_status=status.HTTP_403_FORBIDDEN)

    def test_delete(self):
        self.assert_response(
            get_recipe_url(self.recipe2.pk), method='delete',
            login_as=self.user1,
            expected_status=status.HTTP_204_NO_CONTENT)

    def test_delete_no_auth(self):
        self.assert_response(
            get_recipe_url(self.recipe1.pk), method='delete',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_delete_not_found(self):
        self.assert_response(
            get_recipe_url(99999999), method='delete',
            login_as=self.user1,
            expected_status=status.HTTP_404_NOT_FOUND)

    def test_delete_other_users_recipe(self):
        self.assert_response(
            get_recipe_url(self.recipe3.pk), method='delete',
            login_as=self.user1,
            expected_status=status.HTTP_403_FORBIDDEN)

    def test_short_link(self):
        self.assert_response(
            get_recipe_url(self.recipe1.pk) + 'get-link/',
            expected_data={
                'short-link': f'http://testserver/s/{self.recipe1.pk}'
            })

    def test_short_link_not_found(self):
        self.assert_response(
            get_recipe_url(99999999) + 'get-link/',
            expected_status=status.HTTP_404_NOT_FOUND)
