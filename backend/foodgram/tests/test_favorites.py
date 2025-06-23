from .utils import (
    APIResponseTestCase, status,
    create_user, create_recipe, get_recipe_json_short
)


def get_favorite_url(recipe_id):
    return f'/api/recipes/{recipe_id}/favorite/'


class FavoritesTestCase(APIResponseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = create_user('test_fav_user_1')
        cls.user2 = create_user('test_fav_user_2')
        cls.recipe1 = create_recipe('test_fav_recipe_1', cls.user2)
        cls.recipe2 = create_recipe('test_fav_recipe_2', cls.user2)
        cls.user1.favorites.create(user=cls.user1, recipe=cls.recipe1)

    def test_add(self):
        self.assert_response(
            get_favorite_url(self.recipe2.pk), method='post',
            login_as=self.user1,
            expected_status=status.HTTP_201_CREATED,
            expected_data=get_recipe_json_short(self.recipe2))

    def test_add_not_found(self):
        self.assert_response(
            get_favorite_url(99999999), method='post',
            login_as=self.user1,
            expected_status=status.HTTP_404_NOT_FOUND)

    def test_add_no_auth(self):
        self.assert_response(
            get_favorite_url(self.recipe1.pk), method='post',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_already_added(self):
        self.assert_response(
            get_favorite_url(self.recipe1.pk), method='post',
            login_as=self.user1,
            expected_status=status.HTTP_400_BAD_REQUEST)

    def test_remove(self):
        self.assert_response(
            get_favorite_url(self.recipe1.pk), method='delete',
            login_as=self.user1,
            expected_status=status.HTTP_204_NO_CONTENT)

    def test_remove_not_found(self):
        self.assert_response(
            get_favorite_url(99999999), method='delete',
            login_as=self.user1,
            expected_status=status.HTTP_404_NOT_FOUND)

    def test_remove_no_auth(self):
        self.assert_response(
            get_favorite_url(self.recipe1.pk), method='delete',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_already_removed(self):
        self.assert_response(
            get_favorite_url(self.recipe2.pk), method='delete',
            login_as=self.user1,
            expected_status=status.HTTP_400_BAD_REQUEST)
