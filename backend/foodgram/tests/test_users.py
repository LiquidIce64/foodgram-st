from .utils import (
    APIResponseTestCase, status,
    create_user, get_user_json, get_user_json_short
)


class UserTestCase(APIResponseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = create_user('test_user1')
        cls.user2 = create_user('test_user2')
        cls.user3 = create_user('test_user3')

    def test_list(self):
        self.assert_response(
            '/api/users/',
            expected_data={
                'results': [
                    get_user_json(user=self.user1),
                    get_user_json(user=self.user2),
                    get_user_json(user=self.user3)
                ]
            })

    def test_create(self):
        self.assert_response(
            '/api/users/', method='post',
            data={
                'email': f'test_user4@example.com',
                'username': 'test_user4',
                'first_name': 'test',
                'last_name': 'user',
                'password': 'foodgram_test',
            },
            expected_status=status.HTTP_201_CREATED,
            expected_data=get_user_json_short(4, 'test_user4'))
