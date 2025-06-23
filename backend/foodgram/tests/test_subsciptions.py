from .utils import (
    APIResponseTestCase, status,
    create_user, create_recipe, get_user_json, get_recipe_json_short
)


def get_subscribe_url(user_id):
    return f'/api/users/{user_id}/subscribe/'


URL_SUBSCRIPTIONS = '/api/users/subscriptions/'


class SubscriptionTestCase(APIResponseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = create_user('test_sub_user_1')
        cls.user2 = create_user('test_sub_user_2')
        cls.user3 = create_user('test_sub_user_3')
        cls.user4 = create_user('test_sub_user_4')
        cls.user1.subscriptions.create(user=cls.user1, subscribed_to=cls.user2)
        cls.user1.subscriptions.create(user=cls.user1, subscribed_to=cls.user3)
        cls.user1.subscriptions.create(user=cls.user1, subscribed_to=cls.user4)
        cls.recipe1 = create_recipe('test_sub_recipe_1', cls.user2)
        cls.recipe2 = create_recipe('test_sub_recipe_2', cls.user2)

    def test_list(self):
        self.assert_response(
            URL_SUBSCRIPTIONS,
            login_as=self.user1,
            expected_data={
                'results': [
                    get_user_json(
                        user=self.user2,
                        subscribed=True,
                        recipes_count=2,
                        recipes=[
                            get_recipe_json_short(self.recipe2),
                            get_recipe_json_short(self.recipe1)
                        ]),
                    get_user_json(
                        user=self.user3,
                        subscribed=True,
                        recipes_count=0,
                        recipes=[]),
                    get_user_json(
                        user=self.user4,
                        subscribed=True,
                        recipes_count=0,
                        recipes=[])
                ]
            })

    def test_list_pagination(self):
        self.assert_response(
            URL_SUBSCRIPTIONS + '?limit=1&page=2',
            login_as=self.user1,
            expected_data={
                'count': 3,
                'next': 'http://testserver' + URL_SUBSCRIPTIONS + '?limit=1&page=3',
                'previous': 'http://testserver' + URL_SUBSCRIPTIONS + '?limit=1',
                'results': [
                    get_user_json(
                        user=self.user3,
                        subscribed=True,
                        recipes_count=0,
                        recipes=[])
                ]
            })

    def test_list_recipe_limit(self):
        response = self.assert_response(
            URL_SUBSCRIPTIONS + '?recipes_limit=1',
            login_as=self.user1)
        self.assertEqual(response.data['results'][0]['recipes'], [get_recipe_json_short(self.recipe2)])

    def test_list_no_auth(self):
        self.assert_response(
            URL_SUBSCRIPTIONS,
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_subscribe(self):
        self.assert_response(
            get_subscribe_url(self.user1.pk), method='post',
            login_as=self.user2,
            expected_status=status.HTTP_201_CREATED,
            expected_data=get_user_json(
                user=self.user1,
                subscribed=True,
                recipes_count=0,
                recipes=[]
            ))

    def test_subscribe_recipe_limit(self):
        self.assert_response(
            get_subscribe_url(self.user2.pk) + '?recipes_limit=1', method='post',
            login_as=self.user3,
            expected_status=status.HTTP_201_CREATED,
            expected_data={
                'recipes': [get_recipe_json_short(self.recipe2)]
            })

    def test_subscribe_not_found(self):
        self.assert_response(
            get_subscribe_url(99999999), method='post',
            login_as=self.user1,
            expected_status=status.HTTP_404_NOT_FOUND)

    def test_subscribe_no_auth(self):
        self.assert_response(
            get_subscribe_url(self.user1.pk), method='post',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_subscribe_self(self):
        self.assert_response(
            get_subscribe_url(self.user1.pk), method='post',
            login_as=self.user1,
            expected_status=status.HTTP_400_BAD_REQUEST)

    def test_already_subscribed(self):
        self.assert_response(
            get_subscribe_url(self.user3.pk), method='post',
            login_as=self.user1,
            expected_status=status.HTTP_400_BAD_REQUEST)

    def test_unsubscribe(self):
        self.assert_response(
            get_subscribe_url(self.user3.pk), method='delete',
            login_as=self.user1,
            expected_status=status.HTTP_204_NO_CONTENT)

    def test_unsubscribe_not_found(self):
        self.assert_response(
            get_subscribe_url(99999999), method='delete',
            login_as=self.user1,
            expected_status=status.HTTP_404_NOT_FOUND)

    def test_unsubscribe_no_auth(self):
        self.assert_response(
            get_subscribe_url(self.user1.pk), method='delete',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_unsubscribe_self(self):
        self.assert_response(
            get_subscribe_url(self.user1.pk), method='delete',
            login_as=self.user1,
            expected_status=status.HTTP_400_BAD_REQUEST)
