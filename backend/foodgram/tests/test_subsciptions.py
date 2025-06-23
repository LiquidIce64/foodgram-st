from .utils import APIResponseTestCase, status, create_user, get_user_json


def get_subscribe_url(user_id):
    return f'/api/users/{user_id}/subscribe/'


URL_SUBSCRIPTIONS = '/api/users/subscriptions/'


class SubscriptionTestCase(APIResponseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = create_user('test_sub_user1')
        cls.user2 = create_user('test_sub_user2')
        cls.user3 = create_user('test_sub_user3')
        cls.user1.subscriptions.create(user=cls.user1, subscribed_to=cls.user2)
        cls.user1.subscriptions.create(user=cls.user1, subscribed_to=cls.user3)

    def test_list(self):
        self.assert_response(
            URL_SUBSCRIPTIONS,
            expected_data={
                'results': [
                    get_user_json(
                        user=self.user2,
                        subscribed=True,
                        recipes_count=0,
                        recipes=[]),
                    get_user_json(
                        user=self.user3,
                        subscribed=True,
                        recipes_count=0,
                        recipes=[])
                ]
            },
            login_as=self.user1)

    def test_list_no_auth(self):
        self.assert_response(
            URL_SUBSCRIPTIONS,
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_subscribe(self):
        self.assert_response(
            get_subscribe_url(self.user1.pk), method='post',
            expected_status=status.HTTP_201_CREATED,
            expected_data=get_user_json(
                user=self.user1,
                subscribed=True,
                recipes_count=0,
                recipes=[]
            ),
            login_as=self.user2)

    def test_subscribe_not_found(self):
        self.assert_response(
            get_subscribe_url(99999999), method='post',
            expected_status=status.HTTP_404_NOT_FOUND,
            login_as=self.user1)

    def test_subscribe_no_auth(self):
        self.assert_response(
            get_subscribe_url(self.user1.pk), method='post',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_subscribe_self(self):
        self.assert_response(
            get_subscribe_url(self.user1.pk), method='post',
            expected_status=status.HTTP_400_BAD_REQUEST,
            login_as=self.user1)

    def test_already_subscribed(self):
        self.assert_response(
            get_subscribe_url(self.user3.pk), method='post',
            expected_status=status.HTTP_400_BAD_REQUEST,
            login_as=self.user1)

    def test_unsubscribe(self):
        self.assert_response(
            get_subscribe_url(self.user3.pk), method='delete',
            expected_status=status.HTTP_204_NO_CONTENT,
            login_as=self.user1)

    def test_unsubscribe_not_found(self):
        self.assert_response(
            get_subscribe_url(99999999), method='delete',
            expected_status=status.HTTP_404_NOT_FOUND,
            login_as=self.user1)

    def test_unsubscribe_no_auth(self):
        self.assert_response(
            get_subscribe_url(self.user1.pk), method='delete',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_unsubscribe_self(self):
        self.assert_response(
            get_subscribe_url(self.user1.pk), method='delete',
            expected_status=status.HTTP_400_BAD_REQUEST,
            login_as=self.user1)
